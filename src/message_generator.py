from datetime import datetime

class MessageGenerator:
    '''
    Class that handles how to generate common messages used to
    send over the UndChain network
    '''
    def __init__(self, message_type: str, message: str) -> None:
        self.version = "2024.08.12" # Need to replace with a method that gets the current version
        self.timestamp: str = datetime.utcnow().isoformat()
        
        self.message_type: str = message_type
        self.message: str = message
        self.signature = self._generate_signature(secret_key='bla')

    def _generate_signature(self, secret_key: str) -> str:
        '''
        TODO: Generates a signature for the message using the encryption module.

        Return: 
            str: The generated signature
        '''
        return "Test signature 🧪"

    def generate(self) -> dict:
        '''
        Generates the final message to be sent to the recipient

        Returns:
            dict: The complete message ready for serialization and transmission
        '''
        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "type": self.message_type,
            "message": self.message,
            "signature": self.signature
        }
    
    @staticmethod
    def serialize(message: dict) -> bytes:
        '''
        Serialize the message to bytes

        Returns:
            bytes: The serialized message.
        '''
        return repr(message).encode('utf-8')
    
    @staticmethod
    def deserialize(data: bytes) -> dict:
        '''
        Deserializes bytes back into the a message dictionary.

        Returns:
            dict: The deserialized message.
        '''
        return eval(data.decode('utf-8'))
    
if __name__ == '__main__':
    msg_gen = MessageGenerator(message_type="JobRequest", message='CoChian:Pages, Type: Storage, Resource:UndChain')
    generated_message = msg_gen.generate()

    # Test serialized and deserialize
    serialized_message = MessageGenerator.serialize(generated_message)
    print(f'Serialized message: {serialized_message}')

    deserialized_message = MessageGenerator.deserialize(serialized_message)
    print(f'Deserialized message: {deserialized_message}')
