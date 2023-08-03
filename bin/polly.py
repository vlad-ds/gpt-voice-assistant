import boto3

VOICE_ID = "Salli"

def text_to_speech(text: str):
    # Create an Amazon Polly client
    polly = boto3.client('polly')
    
    # Set the output format
    output_format = 'mp3'

    # Set the output file name
    output_file = 'output.mp3'

    # Synthesize speech
    response = polly.synthesize_speech(Text=text, VoiceId=VOICE_ID, OutputFormat=output_format)

    # Save the audio to a file
    with open(output_file, 'wb') as f:
        f.write(response['AudioStream'].read())