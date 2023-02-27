import os
import pathspec
import emoji
from fpdf import FPDF
from pathlib import Path
from html import escape
from progress.bar import IncrementalBar

OUTPUT_FORMAT = "Task2_Code_[docNum]_[reg]_[surname]_[first_initial].[fileType]"
HEADER_FOOTER_PADDING = 4
PIPE = "│"
ELBOW = "└──"
TEE = "├──"
PIPE_PREFIX = "│   "
SPACE_PREFIX = "    "


def generateTree(path: Path, depth=0, partentPrefix=""):
    tree = ""
    length = sum(1 for item in path.iterdir())
    i = length - 1
    for f in path.iterdir():
        spacing = SPACE_PREFIX * (depth - 1 if depth > 0 else 0)
        filePrefix = ELBOW if f.is_dir() and (depth > 0 and i == 0) else TEE
        prefix = PIPE_PREFIX if depth > 0 else ""
        tree += f"{prefix}{partentPrefix}{spacing}{filePrefix} {f.name}\n"
        if f.is_dir():
            includeParent = "" if depth > 0 and i == 0 else partentPrefix
            tree += generateTree(f, depth + 1,)
            # includeParent + SPACE_PREFIX + PIPE)
        i -= 1

    return tree


def errorAndExit(message: str):
    print(message)
    exit(1)


def parsePlaceholders(text: str, placeholders: dict):
    parsed = text
    for key, value in placeholders.items():
        parsed = parsed.replace(f"[{key}]", value)
    return parsed


def getFileName(docNum: int, reg: str, surname: str, firstName: str, fileType: str):
    placeholders = {
        "docNum": f"{docNum}",
        "reg": reg,
        "surname": surname.capitalize(),
        "first_initial": firstName[0].capitalize(),
        "fileType": fileType,
    }
    return parsePlaceholders(OUTPUT_FORMAT, placeholders)


def addPadding(text: str, paddingText: str, amount: int):
    padding = paddingText * amount
    return padding + text + padding


def createHeader(fileName: str, paddingText: str):
    return addPadding(f"START {fileName}", paddingText, HEADER_FOOTER_PADDING)


def createFooter(fileName: str, paddingText: str):
    return addPadding(f"END {fileName}", paddingText, HEADER_FOOTER_PADDING)


# writeContent to the final output
# inserts header + footer for START and
# END of file being appended
def writeContentPDF(pdf: FPDF, fileName: str, contents: str):
    try:
        header = createHeader(fileName, "<br>")
        footer = createFooter(fileName, "<br>")
        pdf.write_html(header + contents + footer)
        return False
    except Exception as e:
        print(f"{os.linesep}Failed to add {fileName} to final PDF:")
        print(e)
        return True


def writeContentTxt(name: str, contents: str):
    for encoding in ["UTF-8", "ascii"]:
        try:
            with open(name, mode='w', encoding=encoding) as f:
                return f.write(contents)
        except Exception as e:
            pass


# Check path has been provided by the user
# and that the folder exists
def checkCodePathExists(path: str):
    return os.path.exists(path)


# Get all files to be placed into the PDF
# Follow exclude for files that should be
# ignored in file output
def getCodeFiles(path: str, exclude: list[str]):
    files = Path(path).glob('**/*.*')
    spec = pathspec.PathSpec.from_lines("gitwildmatch", exclude)
    files = [file for file in files if not spec.match_file(str(file))]
    return files


def getExcludePaths():
    if Path(".gitignore").exists():
        return Path(".gitignore").read_text().splitlines()
    return []


# Format file contents into valid HTML to be
# rendered within PDF
def formatPDFContents(contents: str):
    htmlSafe = contents
    emojiRemove = emoji.demojize(htmlSafe)
    replaceNewlines = emojiRemove
    finalText = replaceNewlines.replace("\r\n", "<br>").replace(
        "\n", "<br>").replace(" ", "&nbsp")
    PREFIX = '<div style="white-space: pre;">'
    SUFFIX = '</div style="white-space: pre;">'
    return PREFIX + finalText + SUFFIX


def formatTxtContents(fileName: str, contents: str):
    header = createHeader(fileName, "\n")
    footer = createFooter(fileName, "\n")
    return header + contents + footer


def getFileContents(file: Path):
    for encoding in ["UTF-8", "ascii"]:
        try:
            with file.open(mode='r', encoding=encoding) as f:
                formatted = ""
                for contents in f.readlines():
                    for line in contents.split(os.linesep):
                        line = escape(line)
                        formatted += line
                return formatted
        except Exception as e:
            print(f"{encoding} failed for {file.resolve()}.")


def getInput(text: str):
    while True:
        userInput = input(f"{text}{os.linesep} - ")
        if userInput == "" or userInput.isspace():
            print("Please enter a value!")
            continue
        return userInput


def getPathInput(text: str):
    while True:
        userInput = getInput(text)
        if not checkCodePathExists(userInput):
            print(f"\"{userInput}\" does not exist! Please enter a valid path")
            continue
        return userInput


def main():
    print("Hello, this will generate PDF and txt of your code.")
    # codePath = getPathInput("Where is your code located?")
    # firstName = getInput("What is your first name?")
    # last = getInput("What is your last name?")
    # reg = getInput("What is your reg number?")
    # codePath = "C:\\Users\\297882\\college-2022-23\\projects\\pdf-format\\test"
    codePath = "C:\\Users\\297882\\college-2022-23\\projects\\os-mock-1"
    firstName = "daniel"
    last = "raybone"
    reg = "regnumber"

    excludePaths = getExcludePaths()
    files = getCodeFiles(codePath, excludePaths)
    pdfName = getFileName(1, reg, last, firstName, "pdf")
    txtName = getFileName(2, reg, last, firstName, "txt")

    pdf = FPDF()
    pdf.add_font(fname="FreeMono.ttf")
    pdf.set_font("FreeMono")
    pdf.add_page()

    bar = IncrementalBar('Processing', max=len(files) + 1)
    # treeView = generateTree(Path(codePath))
    treeView = ""
    bar.next()

    txtContents = f"File Structure:\n\n{treeView}\n\n\n"
    a = writeContentPDF(pdf, "File Structure",
                        f"{formatPDFContents(treeView)}")
    if a:
        exit()

    for file in files:
        bar.next()
        bar.message = file.name
        contents = getFileContents(file)

        if type(contents) != str:
            print(f"{os.linesep}Skipped {file.resolve()}")
            continue

        pdfContents = formatPDFContents(contents)
        txtContents += formatTxtContents(file.resolve(), contents)

        writeContentPDF(pdf, file.resolve(), f"<div>{pdfContents}</div>")

    writeContentTxt(txtName, txtContents)
    pdf.output(pdfName)
    bar.finish()


if __name__ == "__main__":
    main()
