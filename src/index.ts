import PDFDocument from "pdfkit";
import fs from "fs";
import inquirer from "inquirer";
import ora, { Ora } from "ora";
import { globby } from "globby";
import { promisify } from "util";
import { resolve } from "path";
const getFile = promisify(fs.readFile);
const loader = ora();

type Questions = {
    codePath: string;
    fileName: string;
};

const __dirname = new URL(".", import.meta.url).pathname.replace("/", "");

const getIgnoreFiles = async () => {
    return (await getFile(resolve(__dirname, "..", ".gitignore"))).toString();
};

const getFiles = async (path: string) =>
    // Not sure why these files dont work with the gitignore format
    globby(["**/*", "!yarn.lock", "!*.ico", "!bin/**/*", "!obj/**/*", "!*.dll", "!debug/**/*"], {
        cwd: path,
        ignoreFiles: await getIgnoreFiles(),
        gitignore: true,
    });

const ensureEndsWith = (end: string, str: string) => (str.endsWith(end) ? str : str + end);

const getInput = async () => {
    const { codePath, ...rest } = await inquirer.prompt<Questions>([
        {
            type: "input",
            name: "codePath",
            message: "Enter the full path to the code to pdfify",
        },
        {
            type: "input",
            name: "fileName",
            message: "Enter the name of the output document",
        },
    ]);

    return { ...rest, codePath: ensureEndsWith("/", codePath.replaceAll("\\", "/")) };
};

type AddTextPdf = {
    pdf: PDFKit.PDFDocument;
    loader: Ora;
    files: string[];
    basePath: string;
};

const addTextPdf = ({ basePath, files, loader, pdf }: AddTextPdf) => {
    loader.start("Starting");
    for (const filePath of files) {
        loader.info(`Placing ${filePath} into PDF`);
        const header = `\n\n\nSTART ${filePath}\n\n\n`;
        const footer = `\n\n\nEND ${filePath}`;
        const contents = fs
            .readFileSync(basePath + filePath, { encoding: "utf8" })
            .toString()
            // Encoding issue I cba to figure out
            // https://github.com/foliojs/pdfkit/issues/606#issuecomment-273312814
            .replaceAll(/\r\n|\r/g, "\n");

        pdf.text(header + contents + footer);
    }
};

(async () => {
    const { fileName, codePath } = await getInput();

    const doc = new PDFDocument();
    doc.pipe(fs.createWriteStream(fileName));

    const files = await getFiles(codePath);

    addTextPdf({
        files,
        loader,
        pdf: doc,
        basePath: codePath,
    });

    doc.end();
    loader.stop();
})();
