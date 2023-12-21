import * as fs from "fs";
import * as path from "path";
import fetch from "node-fetch";

const rawSampleSentences = fs.readFileSync(path.join(__dirname, "sample_sentences.txt"), "utf8");
const sampleSentences: string[] = rawSampleSentences.split("\n");
const output: string = "";

async function getCEFRLevel(sentence: string): Promise<string> {
    const response = await fetch("http://localhost:8000/analyze/cefr", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            content: sentence,
        }),
    });
    const json: any = await response.json();
    return json.meta.grade;
}

function saveTextToFile(text: string, filename: string): void {
    fs.writeFileSync(path.join(__dirname, filename), text);
}

for (const sentence of sampleSentences) {
    getCEFRLevel(sentence).then((level) => {
        output.concat(level);
    });
}