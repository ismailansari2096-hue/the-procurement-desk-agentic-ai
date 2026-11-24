"""
Thread Understanding Agent.
Responsible for message parsing, thread splitting, price and unit normalization,
currency conversion, volume discount detection, and missing information identification.
"""

import re
from typing import Dict, Any, Tuple, Optional
from procurement.policy_engine import PolicyEngine
from procurement.thread_parser import ThreadParser
from agentic.models import ThreadUnderstandingOutput


class ThreadUnderstandingAgent:
    """
    Parses complex, multi-turn procurement emails into structured semantic data.
    """

    VOL_DISCOUNT_REGEX = re.compile(
        r"with\s+a\s+further\s+(\d+)\s*%\s*off\s+for\s+orders\s+of\s+(\d+)\s+([a-zA-Z\s]+?)\s+or\s+more",
        re.I
    )

    # V3 GST Inclusion and Exclusion Patterns
    GST_INCLUSIVE_PATTERNS = [
        re.compile(r"\b(inclusive\s+of\s+GST|including\s+GST|\(?GST\s+included\)?|incl\.?\s+GST)\b", re.I)
    ]
    GST_EXCLUSIVE_PATTERNS = [
        re.compile(r"\b(exclusive\s+of\s+GST|excluding\s+GST|excl\.?\s+GST|\+\s*GST|plus\s+GST|GST\s+extra)\b", re.I)
    ]
    ORIGINAL_GST_PAT = re.compile(r"(inclusive\s+of\s+GST|including\s+GST|\(GST\s+included\))", re.I)

    def __init__(
        self,
        policy_engine: Optional[PolicyEngine] = None,
        enable_refined_discounts: bool = True,
        enable_v3_gst: bool = False,
        enable_v4_word_pricing: bool = False
    ):
        self.pe = policy_engine or PolicyEngine()
        self.parser = ThreadParser(self.pe)
        self.enable_refined_discounts = enable_refined_discounts
        self.enable_v3_gst = enable_v3_gst
        self.enable_v4_word_pricing = enable_v4_word_pricing

    def understand_thread(
        self,
        raw_thread: str,
        supplier_name: str,
        category_id: str,
        thread_date: str,
        quantity: int
    ) -> ThreadUnderstandingOutput:
        """
        Extracts latest offer price, normalized unit INR price, volume discount adjustments,
        and missing information flags.
        """
        latest_msg, earlier_msgs = self.parser.split_messages(raw_thread)

        price_inr, parse_err, debug_info = self.parser.extract_latest_offer(
            raw_thread=raw_thread,
            supplier_name=supplier_name,
            category_id=category_id,
            thread_date=thread_date,
            quantity=quantity
        )

        vol_discount_applied = None

        # Check volume discount if offer parsed successfully and refined discounts enabled
        if self.enable_refined_discounts and price_inr is not None and parse_err is None:
            vol_match = self.VOL_DISCOUNT_REGEX.search(latest_msg)
            if vol_match:
                pct = float(vol_match.group(1))
                threshold_qty = int(vol_match.group(2))
                if quantity >= threshold_qty:
                    price_inr = price_inr * (1.0 - pct / 100.0)
                    vol_discount_applied = f"{pct}% discount applied (Order qty {quantity} >= threshold {threshold_qty})"
                    debug_info["volume_discount"] = vol_discount_applied

        # V3 Refined GST Normalization
        if self.enable_v3_gst and price_inr is not None and parse_err is None:
            is_inclusive = any(pat.search(latest_msg) for pat in self.GST_INCLUSIVE_PATTERNS)
            is_exclusive = any(pat.search(latest_msg) for pat in self.GST_EXCLUSIVE_PATTERNS)
            already_divided = bool(self.ORIGINAL_GST_PAT.search(latest_msg))

            if is_inclusive and not is_exclusive and not already_divided:
                policy = self.pe.get_effective_policy(category_id, thread_date, supplier_name)
                gst_rate = float(policy.get("gst_rate", 0.18))
                price_inr = price_inr / (1.0 + gst_rate)
                debug_info["v3_gst_normalized"] = f"Divided by 1 + {gst_rate}"

        # V4 Word-Based Price Extraction Correction (fixes single-digit teen/decade regex prefix truncation)
        if self.enable_v4_word_pricing:
            has_digit_price = bool(re.search(r"(?:INR|Rs\.?|₹|\$|USD|EUR|€|£|GBP)\s*[\d,]+(?:\.\d+)?", latest_msg))
            if not has_digit_price:
                word_tokens_sorted = r"(?:thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|lakh|lakhs|twelve|eleven|zero|one|two|three|four|five|six|seven|eight|nine|ten)"
                clean_msg = latest_msg.replace("-", " ")
                word_m = re.search(rf"(?:is|quote|offer|can do|at)\s+({word_tokens_sorted}+(?:\s+(?:and\s+)?{word_tokens_sorted}+)*)\s*(?:rupees|inr|rs\.?|dollars|usd|euros|eur|pounds|gbp)?\s*(?:per\s+[a-zA-Z\s]+)?", clean_msg, re.I)
                if word_m:
                    val = self.parser.words_to_number(word_m.group(1))
                    if val and val > 0:
                        policy = self.pe.get_effective_policy(category_id, thread_date, supplier_name)
                        unit = policy.get("unit", "").lower()
                        gst_rate = float(policy.get("gst_rate", 0.18))
                        p_word = val
                        if re.search(r"per\s+dozen", latest_msg, re.I):
                            p_word /= 12.0
                        if category_id == "led-lighting" and re.search(r"per\s+pack", latest_msg, re.I):
                            p_word /= 4.0
                        if category_id == "printer-paper" and re.search(r"per\s+ream", latest_msg, re.I):
                            p_word *= 10.0
                        if "per year" in unit and re.search(r"per\s+month\b|/mo\b", latest_msg, re.I):
                            p_word *= 12.0
                        elif "per month" in unit and re.search(r"per\s+year\b|/yr\b", latest_msg, re.I):
                            p_word /= 12.0
                        # Check GST
                        is_incl = any(pat.search(latest_msg) for pat in self.GST_INCLUSIVE_PATTERNS) or bool(self.ORIGINAL_GST_PAT.search(latest_msg))
                        is_excl = any(pat.search(latest_msg) for pat in self.GST_EXCLUSIVE_PATTERNS)
                        if is_incl and not is_excl:
                            p_word /= (1.0 + gst_rate)
                        price_inr = p_word
                        parse_err = None
                        debug_info["v4_word_price_corrected"] = val

        is_missing = (parse_err == "MISSING_INFO" or price_inr is None)

        currency_detected = debug_info.get("currency", "INR") if debug_info else "INR"

        return ThreadUnderstandingOutput(
            latest_message=latest_msg,
            earlier_messages=earlier_msgs,
            extracted_price=debug_info.get("extracted_price") if debug_info else None,
            currency=currency_detected,
            effective_inr_price=price_inr,
            volume_discount_applied=vol_discount_applied,
            is_missing_info=is_missing,
            parse_error=parse_err,
            debug_details=debug_info or {}
        )
