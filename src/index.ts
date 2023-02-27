import PDFDocument from "pdfkit";
import fs from "fs";
import inquirer from "inquirer";
import glob from "glob";
import { promisify } from "util";
import { resolve } from "path";
const globp = promisify(glob);
const getFile = promisify(fs.readFile);

type Questions = {
    codePath: string;
};

const getIgnoreFiles = async () => (await getFile(resolve(__dirname, "..", ".gitignore"))).toString();

const getFiles = async (path: string) => globp(path /*{ ignore: await getIgnoreFiles() }*/);

(async () => {
    // const { codePath } = await inquirer.prompt<Questions>({
    //     type: "input",
    //     name: "codePath",
    //     message: "Enter the full path to the code to pdfify",
    // });
    const codePath = "C:\\Users\\297882\\Documents\\college-2022-23\\projects\\os-mock-1\\**\\*.*";
    const doc = new PDFDocument();

    doc.pipe(fs.createWriteStream("output.pdf"));

    const files = await getFiles(codePath);
    console.log(codePath);
    console.log(files);
    // doc.text(data.toString());

    doc.end();
})();
