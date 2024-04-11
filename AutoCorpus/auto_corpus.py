# import argparse
import re
import argparse
import torch
from rich.console import Console
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import os 
import random
import time

class AutoCorpus:
    def _load_model(self, model_name, device):
        """
        Load the pre-trained language model and tokenizer.

        Args:
            model_name (str): Name of the pre-trained model.
            device (str): Device to load the model onto.

        Returns:
            model (transformers.PreTrainedModel): Loaded language model.
            tokenizer (transformers.PreTrainedTokenizer): Loaded tokenizer.
        """
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2", quantization_config=quantization_config)
        tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
        return model, tokenizer
        
    def _generate_dialogue_response(self, model, tokenizer, device, messages, max_size):
        """
        Generate response from the language model given the input messages.

        Args:
            model (transformers.PreTrainedModel): Loaded language model.
            tokenizer (transformers.PreTrainedTokenizer): Loaded tokenizer.
            device (str): Device to run the model on.
            messages (list): List of input messages.

        Returns:
            str: Generated response.
        """
        encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")
        model_inputs = encodeds.to(device)
        generated_ids = model.generate(model_inputs, max_new_tokens=max_size, do_sample=False, pad_token_id=50256)
        decoded = tokenizer.batch_decode(generated_ids, skip_special_tokens=False)
        return decoded[0]

    def _get_args(self):

        # Create an argument parser with a description
        parser = argparse.ArgumentParser(description="A tool for automatically generating initial fuzzing input corpus test cases")
        
        # Add command line arguments
        parser.add_argument("--input_folder", "-i", type=str, help="The input folder to base generated corpus files off. If no prompt is given, the folder needs at least 1 file.")
        parser.add_argument("--output_folder", "-o", type=str, help="The folder to save generated corpus files to (will default to input folder).")
        parser.add_argument("--number_of_corpus_files", "-n", type=int, default=5, help="The number of corpus files to generate")
        parser.add_argument("--prompt", "-p", type= str, help="A sentence defining what the corpus files are for. This helps steer generation.")
        parser.add_argument("--size", "-s", type= int, default=500, help="Max size of tokens created by the LLM")
        parser.add_argument("--verbose", "-v", action="store_true", help="Provides verbose outputs")

        # Parse the arguments
        args = parser.parse_args()
        
        # Check if the number of corpus files to generate is above 0
        if args.number_of_corpus_files < 1:
            raise Exception("Number of generated corpus files should be above 0!")

        # Check if neither input folder nor prompt is provided, set input folder to current working directory
        if not args.input_folder and not args.prompt:
            args.input_folder = os.getcwd()
            print("No input or prompt provided, generating prompts from files in CWD: '{}".format(args.input_folder))


        # If an input folder is provided, validate it and set output folder to input folder
        if args.input_folder:
            if not os.path.exists(args.input_folder) or not os.path.isdir(args.input_folder):
                raise Exception("Input folder: '{}' is not valid dir path!".format(args.input_folder))
            
            if not args.output_folder:
                args.output_folder = args.input_folder

        # If a prompt is provided but no output folder, raise an exception
        if args.prompt and not args.output_folder:
            raise Exception("You must provide an output folder when not using an input folder!")

        # Check if the output folder is provided and validate it
        if args.output_folder:
            if not os.path.exists(args.output_folder) or not os.path.isdir(args.output_folder):
                raise Exception("Output folder: '{}' is not a valid directory path!".format(args.output_folder))

        # If an input folder is provided but no prompt, check if it contains at least one file
        if args.input_folder and not args.prompt:
            files = os.listdir(args.input_folder)
            if not files:
                raise Exception("No prompt given (--prompt) and input corpus 0. Either provide a prompt or an initial corpus file.")
        
        return args
    
    def _remove_inst_tags(self, text):
        """
        Remove instruction tags from the given text.

        Args:
            text (str): Input text containing instruction tags.

        Returns:
            str: Text with instruction tags removed.
        """
        pattern = r'\[INST\].*?\[/INST\]'
        clean_text = re.sub(pattern, '', text, flags=re.DOTALL)
        return clean_text.replace("<s>", "").replace("</s>", "").replace("Explanation:", "").strip()

    def sample_inputs(self, input_folder, number=4):
        # Check if the input folder exists
        if not os.path.exists(input_folder):
            raise FileNotFoundError(f"Input folder '{input_folder}' not found")

        # List all files in the input folder
        files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

        # Check if there are enough files to sample
        if len(files) < number:
            number = len(files)

        # Randomly sample 'number' of files
        sampled_files = random.sample(files, number)

        # Read and concatenate contents of sampled files
        sampled_contents = ""
        for file_name in sampled_files:
            file_path = os.path.join(input_folder, file_name)
            with open(file_path, 'r') as file:
                sampled_contents += file.read()

        return sampled_contents

    def entry(self):
        """
        Entry point of the program.
        """
        args = self._get_args()
        console = Console()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model_name = "mistralai/Mistral-7B-Instruct-v0.1"
        model, tokenizer = self._load_model(model_name, device)
        console.clear()

        first_run = True
        tasks = [f"task {n}" for n in range(1, args.number_of_corpus_files+1)]

        # Generate prompt for status
        prompt_text = f"[bold green]Creating {args.number_of_corpus_files} test cases in '{args.output_folder}'"
        if args.prompt:
            # Input files and prompt
            if args.input_folder:
                prompt_text = prompt_text + f" from input folder '{args.input_folder}' and prompt '{args.prompt}'."
            # No input files and just prompt
            else:
                prompt_text = prompt_text + f" from prompt '{args.prompt}'."
        # Just input files
        else:
            prompt_text = prompt_text + f" from input folder '{args.input_folder}."

        console.clear()
        with console.status(prompt_text) as status:
            while tasks:
                # Generate question based on inputs
                question = f""
                if args.prompt:
                    # Input files and prompt
                    if args.input_folder:

                        question = f"You have been asked to create the contents of a valid file for '{args.prompt}'. To follow are several example of other types of file that you should follow the format of the samples, but make sure that your data is unique to the samples and valid - ensure to use different types, formats, etc when possible. Only return the newly generated file contents and no other information. \n Samples: \n {self.sample_inputs(args.input_folder)}"
                    # No input files and just prompt
                    else:
                        # If second run start using others as inpiration
                        if first_run:
                            question = f"You have been asked to create the contents of a valid file for '{args.prompt}'. This file will be used as a corpus and should be a ligitimate version of the file. Only return the newly generated file contents and no other information."
                        else:
                            question = f"You have been asked to create the contents of a valid file for '{args.prompt}'. To follow are several example of other types of file that you should follow the format of the samples, but make sure that your data is unique and valid. Only return the newly generated file contents and no other information. \n Samples: \n {self.sample_inputs(args.input_folder)}"

                # Just input files
                else:
                    question = f"You have been asked to create a new corpus file based off the following file samples. The created file should follow the format of the samples, but make sure that your data is unique to the samples and valid - ensure to use different types, formats, etc when possible. Only return the newly generated file contents and no other information. \n Samples: \n {self.sample_inputs(args.input_folder)}"

                question = question + " Only return the file, no additional commentary or explanation!"

                if args.verbose:
                    console.log(question)

                # Ask LLM for output files
                result = self._generate_dialogue_response(model, tokenizer, device, [{"role": "user", "content": question}], args.size)
                result = self._remove_inst_tags(result)

                if args.verbose:
                    console.log(result)

                # Share progress
                task = tasks.pop(0)

                # Save results to file
                epoch_time = int(time.time())  # Get current epoch time
                file_path = os.path.join(args.output_folder, f"test_case_{task}_{epoch_time}.bin")

                if isinstance(result, bytes):
                    # Write content to the file in binary mode ('wb')
                    with open(file_path, 'wb') as file:
                        file.write(result)
                else:
                    # Convert the string to bytes and then write to the file
                    with open(file_path, 'wb') as file:
                        file.write(result.encode('utf-8')) 

                console.clear()
                console.print(f"[bold green]Finished test case {task} of {args.number_of_corpus_files}!")

                first_run = False

def run():
    auto_corpus = AutoCorpus()
    auto_corpus.entry()

if __name__ == "__main__":
    run()