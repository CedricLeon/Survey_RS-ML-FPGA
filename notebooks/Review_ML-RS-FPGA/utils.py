import re
import tabulate

get_total_in_dict_of_lists = lambda dict: sum([len(dict[tag]) for tag in dict])

def wrap_label(label, maxWidth=15):
    words = label.split(' ')
    wrapped = ""
    line = ""
    for word in words:
        # Calculate the length if we add this word (plus space if line is not empty)
        space_needed = 0 if not line else 1
        if len(line) + len(word) + space_needed <= maxWidth:
            if line:
                line += " " + word
            else:
                line = word
        else:
            if line:
                wrapped += line + "\n"
            # If line was empty, we just place the word without forcing a newline
            line = word
    if line:
        wrapped += line
    return wrapped

def print_pretty_df(df, max_rows=-1):
    if max_rows == -1: max_rows = len(df)
    print(
        tabulate.tabulate(
            df.head(max_rows),
            headers="keys",
            tablefmt="pretty",
        )
    )
    
def parse_string_to_dict(inputString):
    """_summary_
    Transforms a string in a Python dictionnary

    Args:
        inputString (_type_): a "dictionnary" in a string format (with several lines with "<key>: <value>")

    Returns:
        dict[Any, Any]: the dictionnary equivalent to the input string
    """
    resultDict = {}
    lines = inputString.split("\n")

    for line in lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            resultDict[key.strip()] = value.strip()

    return resultDict

def extract_year_from_string(dateSTR) -> int:
    """_summary_
    Extract year from a string date. In Zotero the date can be imported in many different formats.
    For example: "2021-06", "2021", "2024 OCT 15", "2021 JUL", "2022/08/01", etc.
    This function identifies the year as a 4-digit number in the string.

    Args:
        dateSTR (_type_): The date in string format

    Raises:
        ValueError: If no year is found in the string

    Returns:
        int: The year.
    """
    match = re.search(r'(\d{4})', dateSTR)
    if match:
        return int(match.group(1))
    else:
        raise ValueError(f'No year found in "{dateSTR}"')

def find_positions_parentheses_and_braces(fullTagModelName: str) -> tuple[int, int, int, int]:
    """Find the positions of parentheses and braces in the model name string.

    Args:
        fullTagModelName (str): The full model name string.

    Returns:
        tuple[int, int, int, int]: The start and end positions of parentheses and braces.
    """
    parenthesisStart: int = fullTagModelName.find("(")
    parenthesisEnd: int = fullTagModelName.find(")")
    braceStart: int = fullTagModelName.find("{")
    braceEnd: int = fullTagModelName.find("}")

    if (parenthesisStart == -1 and parenthesisEnd != -1) or (
        parenthesisStart != -1 and parenthesisEnd == -1
    ):
        raise ValueError(f"Parentheses are missing in {fullTagModelName}.")
    if (braceStart == -1 and braceEnd != -1) or (braceStart != -1 and braceEnd == -1):
        raise ValueError(f"Braces are missing in {fullTagModelName}.")

    return parenthesisStart, parenthesisEnd, braceStart, braceEnd

def parse_string_parentheses_braces(
    originalStr: str, defaultToStr1: bool = False
) -> tuple[str, str, str]:
    """_summary_
    Parses a string containing parentheses and braces, and returns the 3 components of the string.
    The string is expected in the format: originalStr = "str1 (str2) {str3}".

    Args:
        originalStr (str):  originalStr = "str1 (str2) {str3}"
        defaultToStr1 (bool, optional): Sets str2 and str3 to str1 if empty. Defaults to False.
    Raises:
        ValueError: if Parentheses or Braces are missing in the originalStr

    Returns:
        tuple[str, str, str]: Tuple with the 3 components of the original string
    """
    str1 = ""; str2 = ""; str3 = ""

    # Will raise an error if Parentheses or Braces are missing
    parStart, parEnd, braceStart, braceEnd = (
        find_positions_parentheses_and_braces(originalStr)
    )

    str1: str = originalStr[:parStart].strip()
    str2: str = originalStr[
        parStart + 1 : parEnd
    ].strip()
    str3: str = originalStr[braceStart + 1 : braceEnd].strip()
    if defaultToStr1:
        if str2 == "": str2 = str1
        if str3 == "": str3 = str1

    return str1, str2, str3
