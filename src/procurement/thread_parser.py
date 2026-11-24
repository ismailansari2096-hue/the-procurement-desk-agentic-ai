"""
Thread Parser and Offer Normalizer.
Extracts and normalizes supplier offers according to units-and-currency.md and precedents/.
"""

import re
from typing import Dict, Any, Optional, Tuple, List
from procurement.policy_engine import PolicyEngine


class ThreadParser:
    UNITS_WORDS = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16,
        'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90
    }
    MULTIPLIERS_WORDS = {'hundred': 100, 'thousand': 1000, 'lakh': 100000, 'lakhs': 100000}

    def __init__(self, policy_engine: PolicyEngine):
        self.pe = policy_engine

    def split_messages(self, raw_thread: str) -> Tuple[str, List[str]]:
        """Split thread into latest message and earlier messages."""
        if not raw_thread:
            return "", []

        latest_match = re.search(r"\[Latest message[^\n\]]*\]", raw_thread)
        if latest_match:
            parts = raw_thread.split(latest_match.group(0))
            earlier_text = parts[0]
            latest_text = parts[1].strip() if len(parts) > 1 else ""
            earlier_msgs = [m.strip() for m in re.split(r"\[Earlier message[^\n\]]*\]", earlier_text) if m.strip()]
            return latest_text, earlier_msgs
        else:
            return raw_thread.strip(), []

    def extract_earlier_supplier_quote(self, earlier_msgs: List[str], supplier_name: str) -> Tuple[Optional[float], Optional[str]]:
        """Extract previous supplier quote and billing period from earlier messages."""
        for msg in reversed(earlier_msgs):
            if "Acme Procurement" in msg and supplier_name not in msg:
                continue
            period = None
            if re.search(r"per\s+(year|month|yr|mo)", msg, re.I):
                pm = re.search(r"per\s+(year|month|yr|mo)", msg, re.I)
                period = pm.group(1).lower()

            m = re.search(r"(?:quote\s+(?:is|was)|offer\s+(?:is|was)|can\s+do|at)\s*(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?)", msg, re.I)
            if m:
                val_str = m.group(1).replace(",", "")
                try:
                    return float(val_str), period
                except ValueError:
                    pass
        return None, None

    def words_to_number(self, text: str) -> Optional[float]:
        """Convert English words representation of number to float."""
        cleaned_text = text.replace("-", " ").lower()
        tokens = re.findall(r"[a-zA-Z]+", cleaned_text)
        total = 0.0
        current = 0.0
        found_any = False

        for token in tokens:
            if token in self.UNITS_WORDS:
                current += self.UNITS_WORDS[token]
                found_any = True
            elif token == "hundred":
                if current == 0:
                    current = 1.0
                current *= 100.0
                found_any = True
            elif token in ["thousand", "lakh", "lakhs"]:
                if current == 0:
                    current = 1.0
                total += current * self.MULTIPLIERS_WORDS[token]
                current = 0.0
                found_any = True
            elif token in ["and", "rupees", "inr", "rs", "dollars", "usd", "euros", "eur", "pounds", "gbp"]:
                continue
            else:
                break

        total += current
        return total if found_any else None

    def parse_number(self, num_str: str) -> Optional[float]:
        """Parse number string handling digits, words, lakhs, and k notation."""
        if not num_str:
            return None
        cleaned = num_str.replace(",", "").strip().lower()

        # Check digits first
        if re.search(r"\d", cleaned):
            if "lakh" in cleaned:
                val_part = re.search(r"([\d.]+)", cleaned)
                if val_part:
                    return float(val_part.group(1)) * 100000.0
            elif "k" in cleaned:
                val_part = re.search(r"([\d.]+)", cleaned)
                if val_part:
                    return float(val_part.group(1)) * 1000.0
            else:
                val_part = re.search(r"([\d.]+)", cleaned)
                if val_part:
                    return float(val_part.group(1))
        else:
            # Try words to number
            return self.words_to_number(cleaned)

        return None

    def extract_latest_offer(
        self,
        raw_thread: str,
        supplier_name: str,
        category_id: str,
        thread_date: str,
        quantity: int
    ) -> Tuple[Optional[float], Optional[str], Dict[str, Any]]:
        """
        Parses supplier's current offer.
        Returns:
            (normalized_price, error_reason, debug_info)
        """
        latest_msg, earlier_msgs = self.split_messages(raw_thread)
        policy = self.pe.get_effective_policy(category_id, thread_date, supplier_name)
        unit = policy.get("unit", "").lower()
        gst_rate = policy.get("gst_rate", 0.18)

        debug = {
            "latest_msg": latest_msg,
            "earlier_msgs_count": len(earlier_msgs),
            "policy": policy
        }

        # Check for unlisted foreign currency
        unlisted_curr_match = re.search(r"\b(JPY|SGD|AUD|CAD|CHF|CNY|AED|SAR|NZD)\b", latest_msg, re.I)
        if unlisted_curr_match:
            unlisted = unlisted_curr_match.group(1).upper()
            if not self.pe.get_exchange_rate(unlisted, supplier_name):
                return None, "MISSING_INFO", debug

        # Check subscription without billing period
        # Precedent P-06: Subscriptions (cloud-servers, crm-licenses, design-software)
        is_subscription = category_id in ["cloud-servers", "crm-licenses", "design-software"]
        has_earlier_discount = bool(re.search(r"discount\s+on\s+our\s+previous\s+quote|off\s+our\s+previous\s+quote", latest_msg, re.I))

        if is_subscription and not has_earlier_discount and not re.search(r"in\s+total\s+for\s+all", latest_msg, re.I):
            has_explicit_period = bool(re.search(r"(per\s+(year|month|yr|mo)|per\s+seat\s+per\s+(year|month)|per\s+server\s+per\s+(year|month)|\/yr|\/mo)", latest_msg, re.I))
            if not has_explicit_period:
                return None, "MISSING_INFO", debug

        # Check currency
        currency = "INR"
        if re.search(r"\bUSD\b|\$", latest_msg):
            currency = "USD"
        elif re.search(r"\bEUR\b|€", latest_msg):
            currency = "EUR"
        elif re.search(r"\bGBP\b|£", latest_msg):
            currency = "GBP"

        fx_rate = self.pe.get_exchange_rate(currency, supplier_name)
        if fx_rate is None:
            return None, "MISSING_INFO", debug

        raw_price = None

        # 1. Check for CORRECTION
        correction_match = re.search(r"CORRECTION\s*—\s*the\s+price[^\n]*?should\s+read\s*(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?(?:\s*lakh|\s*k)?)", latest_msg, re.I)
        if correction_match:
            raw_price = self.parse_number(correction_match.group(1))

        # 2. Check for discount on previous quote: "a further 5% off our previous quote", "10% discount on our previous quote"
        elif re.search(r"(\d+)\s*%\s*(?:discount\s+on|off)\s+our\s+previous\s+quote", latest_msg, re.I):
            pct_m = re.search(r"(\d+)\s*%\s*(?:discount\s+on|off)\s+our\s+previous\s+quote", latest_msg, re.I)
            pct = float(pct_m.group(1))
            earlier_quote, earlier_period = self.extract_earlier_supplier_quote(earlier_msgs, supplier_name)
            if earlier_quote is not None:
                raw_price = earlier_quote * (1.0 - pct / 100.0)

        # 3. Check for discount on list price: "10% discount on our list price of INR 410"
        elif re.search(r"(\d+)\s*%\s*discount\s+on\s+our\s+list\s+price\s+of\s*(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?(?:\s*lakh|\s*k)?)", latest_msg, re.I):
            disc_m = re.search(r"(\d+)\s*%\s*discount\s+on\s+our\s+list\s+price\s+of\s*(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?(?:\s*lakh|\s*k)?)", latest_msg, re.I)
            pct = float(disc_m.group(1))
            list_price = self.parse_number(disc_m.group(2))
            if list_price:
                raw_price = list_price * (1.0 - pct / 100.0)

        # 4. Check for range: "between Rs. 1,506 and ₹1,638 per fixture"
        elif re.search(r"between\s*(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?)\s*and\s*(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?(?:\s*lakh|\s*k)?)", latest_msg, re.I):
            range_m = re.search(r"between\s*(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?)\s*and\s*(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?(?:\s*lakh|\s*k)?)", latest_msg, re.I)
            # Precedent P-01, P-04: always take the upper bound
            raw_price = self.parse_number(range_m.group(2))

        # 5. Check for tiered pricing: "INR 28,518 per phone for orders of up to 20 phones, and INR 27,200 per phone for larger orders"
        elif re.search(r"for\s+orders\s+of\s+up\s+to\s+(\d+)\s+[^,\n]+,\s*and\s*(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?)\s*per\s+[^\n,]+\s*for\s+larger\s+orders", latest_msg, re.I):
            tiered_m = re.search(r"(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?)\s*per\s+[^\n,]+\s*for\s+orders\s+of\s+up\s+to\s+(\d+)\s+[^,\n]+,\s*and\s*(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?)\s*per\s+[^\n,]+\s*for\s+larger\s+orders", latest_msg, re.I)
            if tiered_m:
                tier1_price = self.parse_number(tiered_m.group(1))
                tier1_limit = int(tiered_m.group(2))
                tier2_price = self.parse_number(tiered_m.group(3))
                if quantity <= tier1_limit:
                    raw_price = tier1_price
                else:
                    raw_price = tier2_price

        # 6. Check for total price: "₹44,07,800 in total for all 60 laptops"
        elif re.search(r"(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?(?:\s*lakh|\s*k)?)\s*in\s+total\s+for\s+all\s+(\d+)", latest_msg, re.I):
            total_m = re.search(r"(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?(?:\s*lakh|\s*k)?)\s*in\s+total\s+for\s+all\s+(\d+)", latest_msg, re.I)
            total_amount = self.parse_number(total_m.group(1))
            total_qty = int(total_m.group(2))
            if total_amount and total_qty > 0:
                raw_price = total_amount / float(total_qty)

        # 7. Check for general quote per unit with digits: "quote Rs. 12,662 per monitor", "can do INR 78,801 per laptop"
        elif re.search(r"(?:quote|offer|can do|price is)\s*(?:is|was)?\s*(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?(?:\s*lakh|\s*k)?)\s*per\s+([a-zA-Z\s]+)", latest_msg, re.I):
            unit_m = re.search(r"(?:quote|offer|can do|price is)\s*(?:is|was)?\s*(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)?\s*([\d,]+(?:\.\d+)?(?:\s*lakh|\s*k)?)\s*per\s+([a-zA-Z\s]+)", latest_msg, re.I)
            raw_price = self.parse_number(unit_m.group(1))

        # 8. Check for quote with amount in words: e.g. "two hundred sixty-six rupees per meal"
        if raw_price is None:
            word_tokens = r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|lakh|lakhs|and)"
            clean_msg_for_words = latest_msg.replace("-", " ")
            word_quote_m = re.search(rf"(?:is|quote|offer|can do|at)\s+({word_tokens}+(?:\s+{word_tokens}+)*)\s*(?:rupees|inr|rs\.?|dollars|usd|euros|eur|pounds|gbp)?\s*(?:per\s+[a-zA-Z\s]+)?", clean_msg_for_words, re.I)
            if word_quote_m:
                raw_price = self.words_to_number(word_quote_m.group(1))

        # 9. Fallback: find any currency + number in latest message
        if raw_price is None:
            fb_m = re.search(r"(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)\s*([\d,]+(?:\.\d+)?(?:\s*lakh|\s*k)?)", latest_msg, re.I)
            if fb_m:
                raw_price = self.parse_number(fb_m.group(1))

        if raw_price is None or raw_price <= 0:
            return None, "MISSING_INFO", debug

        # Convert FX to INR
        price_inr = raw_price * fx_rate

        # Check for free unit concession: "plus 1 free meal for every 10 you pay for"
        free_m = re.search(r"plus\s+1\s+free\s+\w+\s+for\s+every\s+(\d+)\s+you\s+pay\s+for", latest_msg, re.I)
        if free_m:
            paid_n = int(free_m.group(1))
            # Precedent P-02, P-05: Effective price = price * paid_n / (paid_n + 1)
            price_inr = price_inr * (float(paid_n) / (paid_n + 1.0))

        # Check pack conversions / sub-units
        # "per dozen" -> divide by 12
        if re.search(r"per\s+dozen", latest_msg, re.I):
            price_inr = price_inr / 12.0

        # Category pack conversions:
        # LED lighting: 1 pack = 4 fixtures
        if category_id == "led-lighting" and re.search(r"per\s+pack", latest_msg, re.I):
            price_inr = price_inr / 4.0

        # Printer paper: 1 box = 10 reams
        if category_id == "printer-paper" and re.search(r"per\s+ream", latest_msg, re.I):
            price_inr = price_inr * 10.0

        # Check subscription monthly <-> yearly normalization
        # "per seat per month" when unit is "per seat per year" -> x 12
        if "per year" in unit and re.search(r"per\s+month\b|/mo\b", latest_msg, re.I):
            price_inr = price_inr * 12.0
        elif "per month" in unit and re.search(r"per\s+year\b|/yr\b", latest_msg, re.I):
            price_inr = price_inr / 12.0

        # Check GST inclusion: if inclusive of GST -> divide by (1 + gst_rate)
        if re.search(r"(inclusive\s+of\s+GST|including\s+GST|\(GST\s+included\))", latest_msg, re.I):
            price_inr = price_inr / (1.0 + gst_rate)

        return price_inr, None, debug
