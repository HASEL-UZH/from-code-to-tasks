from transformers import LlamaForCausalLM, CodeLlamaTokenizer




def generate_text():
    # Load the pre-trained Code Llama model and tokenizer
    model_name = "codellama/CodeLlama-7b-hf"
    print('before')
    model = LlamaForCausalLM.from_pretrained(model_name)
    print('after')
    tokenizer = CodeLlamaTokenizer.from_pretrained(model_name)

    code_prompt = '''
    def example_function():
        # Your code prompt here
        for i in range(10):
            print("Iteration:", i)
    '''

    # Tokenize the code prompt
    input_ids = tokenizer.encode(code_prompt, return_tensors="pt", padding=True, truncation=True)

    # Generate text based on the tokenized code prompt
    generated_ids = model.generate(input_ids, max_length=50, num_return_sequences=1)

    # Decode the generated text to obtain the human-readable output
    generated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    return generated_text


if __name__ == '__main__':
   print("generated text: " + generate_text())
