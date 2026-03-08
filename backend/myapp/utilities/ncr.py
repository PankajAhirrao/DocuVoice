import re
from collections import defaultdict

# Optional spaCy (keep app runnable without it)
try:
    import spacy  # type: ignore
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        nlp = None
except Exception:
    spacy = None
    nlp = None

def extract_legal_entities(text):
    # Initialize entity dictionary
    entities = defaultdict(list)

    # Extract entities from spaCy if available
    if nlp is not None and text:
        try:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "DATE":
                    if ent.text not in entities["DATE"]:
                        entities["DATE"].append(ent.text)
                elif ent.label_ == "PERSON":
                    if ent.text not in entities["PERSON"]:
                        entities["PERSON"].append(ent.text)
                elif ent.label_ == "ORG":
                    if ent.text not in entities["ORGANIZATION"]:
                        entities["ORGANIZATION"].append(ent.text)
                elif ent.label_ == "GPE":
                    if ent.text not in entities["LOCATION"]:
                        entities["LOCATION"].append(ent.text)
                elif ent.label_ == "MONEY":
                    if ent.text not in entities["MONEY"]:
                        entities["MONEY"].append(ent.text)
        except Exception:
            pass
    
    # Improved pattern-based extraction for legal-specific entities
    
    # Case Numbers - Expanded to include more formats and abbreviations
    case_patterns = [
        r'(?:Appeal|Petition|Civil|Criminal|Writ|Revision)\s+No\.\s+\d+\s+of\s+\d{4}',
        r'(?:C|W|P)\.P\.\s+No\.\s+\d+\s+of\s+\d{4}',
        r'[A-Z]\.?[A-Z]\.?\s+No\.?\s*\d+\s+of\s+\d{4}',
        r'[A-Z]\.?[A-Z]\.?\s+No\.?\s*\d+/\d{4}',
        r'(?:Appeal|Civil|Criminal|Writ|Revision|Petition)\s+No\.?\s*\d+/\d{4}',
        # Specific patterns for M.P. type references
        r'M\.P\.?\s+No\.?\s*\d+\s+of\s+\d{4}',
        r'Crl\.?\s*M\.P\.?\s+No\.?\s*\d+\s+of\s+\d{4}',
        r'C\.?M\.P\.?\s+No\.?\s*\d+\s+of\s+\d{4}',
        r'[A-Z](?:\.[A-Z])+\.?\s+No\.?\s*\d+\s+of\s+\d{4}',
        # Capture just numbers after clear case identifiers
        r'(?:No\.|Number)\s*\d+\s+of\s+\d{4}',
        # Various abbreviations with numbers
        r'(?:SLP|CWP|CRP|FAO|RFA|RSA|CRA|CRR|WA|SA|CA|CP|TP|RP|SPLP|OA|IA|WPC|WP|SP)\s*\(?C\)?\s*No\.?\s*\d+(?:/\d+)?\s+of\s+\d{4}',
        # Formats with section references
        r'[A-Z]\.?[A-Z]\.?\s+No\.?\s*\d+.{0,20}?section\s+\d+.{0,20}?[A-Z]\.?[A-Z]\.?'
    ]
    
    for pattern in case_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            case_number = match.group().strip()
            if case_number and case_number not in entities["CASE_NUMBER"]:
                entities["CASE_NUMBER"].append(case_number)
    
    # Courts - Expanded patterns
    court_patterns = [
        r'(?:Supreme|High|District|Sessions|Metropolitan|Magistrate\'s|Family|Juvenile|Tribunal)\s+Court',
        r'(?:[A-Z][a-z]+(?:\s+and\s+[A-Z][a-z]+)?)\s+High\s+Court',
        r'Court\s+of\s+Session',
        r'Chief\s+(?:Judicial|Metropolitan)\s+Magistrate',
        # Common abbreviations
        r'(?:CJM|CMM|ACJM|ACMM)',
        r'\d+(?:st|nd|rd|th)\s+(?:Addl\.|Additional)\s+(?:Sessions|Metropolitan|Judicial)\s+(?:Judge|Magistrate)'
    ]
    
    for pattern in court_patterns:
        for match in re.finditer(pattern, text):
            court = match.group().strip()
            if court and court not in entities["COURT"]:
                entities["COURT"].append(court)
    
    # Judges - Expanded patterns
    judge_patterns = [
        r'[A-Z][a-z]+,\s+(?:C\.J\.|J\.)',
        r'Justice\s+[A-Z][a-z]+',
        r'[A-Z][a-z]+\s+[A-Z][a-z]+,\s+(?:C\.J\.|J\.)',
        r'Hon\'ble\s+(?:Justice|Judge|Mr\.|Ms\.|Mrs\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?'
    ]
    
    for pattern in judge_patterns:
        for match in re.finditer(pattern, text):
            judge = match.group().strip()
            if judge and judge not in entities["JUDGE"]:
                entities["JUDGE"].append(judge)
    
    # Statutes - Expanded
    statute_patterns = [
        r'(?:[A-Z][a-z]+\s+){1,3}Act,\s+\d{4}',
        r'(?:[A-Z][a-z]+\s+){1,3}Act',
        r'(?:[A-Z][a-z]+\s+){1,3}Code',
        r'(?:IPC|CrPC|CPC|I\.P\.C\.|Cr\.P\.C\.|C\.P\.C\.)'
    ]
    
    for pattern in statute_patterns:
        for match in re.finditer(pattern, text):
            statute = match.group().strip()
            if statute and statute not in entities["STATUTE"]:
                entities["STATUTE"].append(statute)
    
    # Legal provisions - Expanded
    provision_patterns = [
        r'[Ss]ection\s+\d+(?:\(\w+\))?(?:\s+of\s+the\s+(?:[A-Z][a-z]+\s+){1,3}(?:Act|Code))?',
        r'[Aa]rticle\s+\d+(?:\(\w+\))?',
        r'[Ss]\.\s*\d+(?:\(\w+\))?',
        r'[Ss][Ss]\.\s*\d+(?:\(\w+\))?',
        # Add specific pattern for section 482 CrPC
        r'[Ss]ection\s+482\s+of\s+the\s+Cr\.\s*P\.\s*C\.?',
        r'[Ss]ection\s+482\s+Cr\.\s*P\.\s*C\.?',
        r'[Ss]ec\.\s+482\s+Cr\.\s*P\.\s*C\.?'
    ]
    
    for pattern in provision_patterns:
        for match in re.finditer(pattern, text):
            provision = match.group().strip()
            if provision and provision not in entities["PROVISION"]:
                entities["PROVISION"].append(provision)
    
    # Convert defaultdict to regular dict and remove empty categories
    return {k: v for k, v in entities.items() if v}

def print_entities(entities):
    print("LEGAL ENTITIES EXTRACTED:")
    print("=" * 50)
    
    for entity_type, items in sorted(entities.items()):
        print(f"\n{entity_type} ({len(items)}):")
        print("-" * 30)
        for item in sorted(items):
            print(f"  • {item}")

# Test with your specific example
# test_text = "M.P. No.2717 of 1988 in the High Court under section 482 of the Cr. P.C."

# # Process the document
# entities = extract_legal_entities(test_text)

# # Display results
# print_entities(entities)

# # Test with the longer example as well
# legal_text = """
# Appeal No. 623 of 1975. From the Judgment and Order dated 25 June 1974 of the Karnataka 
# High Court in Civil Revision No. 1981/73. The Judgment of the Court was delivered by 
# RAY, C.J. on 15 January 1976.

# This appeal by special leave is from the judgment dated 25 June, 1974 of the Karnataka 
# High Court. The principal question in this appeal is whether section 107 of the Karnataka 
# Land Reforms Act, 1961 applies to the land in suit which was leased to the respondent.

# Cr. M.P. No.2717 of 1988 in the High Court under section 482 of the Cr. P.C. was filed
# challenging the jurisdiction of the court.

# S.S. Javali and B.P. Singh appeared for the Appellants.
# S.V. Gupte and K.N. Bhatt appeared for the Respondent.
# """

# # Process the document
# entities2 = extract_legal_entities(legal_text)

# # Display results
# print("\n\nFull Text Analysis:")
# print_entities(entities2)