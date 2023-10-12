from transformers import PLBartForConditionalGeneration, PLBartTokenizer

def translate_python_to_english():
    model_name = "uclanlp/plbart-java-en_XX"
    tokenizer = PLBartTokenizer.from_pretrained(model_name)
    model = PLBartForConditionalGeneration.from_pretrained(model_name)

    # Define Java code
    java_code = 'public static int minimum(int a, int b, int c) {return Math.max(Math.max(a, b), c);}'

    # Encode the source text (Java code) in the required format
    src_text = f"{java_code} [eos, java]"

    # Define generation parameters
    generation_params = {
        'max_length': 100,  # Adjust the max length based on your preference
        'num_beams': 7,
        'length_penalty': 1.0,
        'early_stopping': True,
    }

    # Generate English translation
    translated_tokens = model.generate(tokenizer(src_text, return_tensors="pt").input_ids,  **generation_params)

    # Decode the translated tokens to get the translated English text
    translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

    return translated_text

if __name__ == '__main__':
    translated_text = translate_python_to_english()
    print("Translated English text:")
    print(translated_text)





