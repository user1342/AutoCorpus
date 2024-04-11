<p align="center">
    <img width=100% src="logo.gif">
  </a>
</p>
<p align="center"> 🤖 Automated Fuzzing Corpus Generation 📁 </p>

<div align="center">

![GitHub contributors](https://img.shields.io/github/contributors/user1342/AutoCorpus)
![GitHub Repo stars](https://img.shields.io/github/stars/user1342/AutoCorpus?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/user1342/AutoCorpus?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/user1342/AutoCorpus)
<br>

</div>

AutoCorpus is a tool backed by a large language model (LLM) for automatically generating corpus files for fuzzing. 

AutoCorpus works best when generating corpus files that are based om natural language, such as JSON, XML, or other config files. 

# ⚙️ Setup

## System Requirements
AutoCorpus utilizes the Mistral-7B-Instruct-v0.2 model and, where possible, offloads processing to your system's GPU. It is recommended to run AutoCorpus on a machine with a minimum of 16GB of RAM and a dedicated Nvidia GPU with at least 4GB of memory. However, it can run on lower-spec machines, albeit at a significantly slower pace.

**AutoCorpus has been tested on Windows 11; however, it should be compatible with Unix and other systems.**

## Dependencies
AutoCorpus requires **Nvidia CUDA** for enhanced LLM performance. Follow the steps below:
- Ensure your Nvidia drivers are up to date: [Nvidia Drivers](https://www.nvidia.com/en-us/geforce/drivers/)
- Install the appropriate dependencies from [here](https://pytorch.org/get-started/locally/)
- Validate CUDA installation by running the following command and receiving a prompt: ```python -c "import torch; print(torch.rand(2,3).cuda())"```

Python dependencies can be found in the `requirements.txt` file:

```
pip install -r requirements.txt
```

AutoCorpus can then be installed using the ```./setup.py``` script as below:

```
python -m pip install .
```

## Running

AutoCorpus can generate corpus files via three different scenarios:

### A Single Prompt
For example asking AutoCorpus to generate an XML file would be as follows:
```
AutoCorpus.exe -o "out" -p "xml file"
```
### Existing Corpus File(s)
AutoCorpus can base new corpus files off existing ones.
```
AutoCorpus.exe -i "input_folder" -o "out"
```
### Both Existing Corpus Files And a Prompt.
Generation can be run by using both an existing corpus and a prompt.
```
AutoCorpus.exe -i "input_folder" -o "out" -p "xml file"
```

### Usage
```
usage: AutoCorpus [-h] [--input_folder INPUT_FOLDER] [--output_folder OUTPUT_FOLDER] [--number_of_corpus_files NUMBER_OF_CORPUS_FILES] [--prompt PROMPT]
                  [--size SIZE] [--verbose]

A tool for automatically generating initial fuzzing input corpus test cases

optional arguments:
  -h, --help            show this help message and exit
  --input_folder INPUT_FOLDER, -i INPUT_FOLDER
                        The input folder to base generated corpus files off. If no prompt is given, the folder needs at least 1 file.
  --output_folder OUTPUT_FOLDER, -o OUTPUT_FOLDER
                        The folder to save generated corpus files to (will default to input folder).
  --number_of_corpus_files NUMBER_OF_CORPUS_FILES, -n NUMBER_OF_CORPUS_FILES
                        The number of corpus files to generate
  --prompt PROMPT, -p PROMPT
                        A sentence defining what the corpus files are for. This helps steer generation.
  --size SIZE, -s SIZE  Max size of tokens created by the LLM
  --verbose, -v         Provides verbose outputs
```

### Examples

#### JSON Corpus Generation
Generates 5 corpus files solely on the prompt ```complex json files with varying data```.
```
AutoCorpus.exe -o "out" -p "complex json files with varying data"
```

```
[{"id": 1, "name": "John Doe", "age": 30, "city": "New York"},

{"id": 2, "name": "Jane Smith", "age": 28, "city": "Los Angeles"},

{"id": 3, "name": "Mike Johnson", "age": 35, "city": "Chicago"},

{"id": 4, "name": "Emma Watson", "age": 27, "city": "London"}]
```

#### AWK Config Corpus Generation

Creates an AWK config based on existing example awk configs in the ``` ..\corpus\awk\``` directory along with the prompt ```config file for busybox awk```.
```
AutoCorpus.exe -i ..\corpus\awk\ -p "config file for busybox awk" -n 10 -s 700
```
```
```bash
#!/usr/bin/awk -f

BEGIN {
  FS="\t"
  if (ARGC != 3) {
    print "Usage: awk-script.awk <file> <field> <delimiter>"
    exit 1
  }
  print "Input file:", ARGV[1]
  print "Field to print:", ARGC[2]
  print "Delimiter:", ARGC[3]

  FILENAME = ARGV[1]
  if (open(FILENAME, "r")) {
    while ((getline line < FILENAME) > 0) {
      gsub(/[[:space:]]+/, "", line) # remove whitespaces
      split(line, fields, FS)
      for (i = 1; i <= NF; i++) {
        if (length(fields[i]) > 0 && fields[i] ~ /\Q"[\"']"ARGV[2]"\Q/ && i != ARGC[3]) {
          next
        }
        if (i == ARGC[3] || i == NF) {
          print fields[i]
          break
        }
      }
    }
    close(FILENAME)
  } else {
    print "Error opening file:", FILENAME
    exit 1
  }
}```
```

# 🤖 Mistral-7B-Instruct-v0.2
Behind the scenes AutoCorpus uses the ```Mistral-7B-Instruct-v0.2``` model from The Mistral AI Team - see [here](https://arxiv.org/abs/2310.06825). The Mistral-7B-Instruct-v0.2 Large Language Model (LLM) is an instruct fine-tuned version of the Mistral-7B-v0.2. More can be found on the model [here!](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2).
- 7.24B params
- Tensor type: BF16
- 32k context window (vs 8k context in v0.1)
- Rope-theta = 1e6
- No Sliding-Window Attention

# 🙏 Contributions
AutoCorpus is an open-source project and welcomes contributions from the community. If you would like to contribute to
AutoCorpus, please follow these guidelines:

- Fork the repository to your own GitHub account.
- Create a new branch with a descriptive name for your contribution.
- Make your changes and test them thoroughly.
- Submit a pull request to the main repository, including a detailed description of your changes and any relevant documentation.
- Wait for feedback from the maintainers and address any comments or suggestions (if any).
- Once your changes have been reviewed and approved, they will be merged into the main repository.

# ⚖️ Code of Conduct
AutoCorpus follows the Contributor Covenant Code of Conduct. Please make sure to review and adhere to this code of conduct when contributing to AutoCorpus.

# 🐛 Bug Reports and Feature Requests
If you encounter a bug or have a suggestion for a new feature, please open an issue in the GitHub repository. Please provide as much detail as possible, including steps to reproduce the issue or a clear description of the proposed feature. Your feedback is valuable and will help improve AutoCorpus for everyone.

# 📜 License

[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)
