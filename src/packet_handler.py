import struct
from logging import Logger
from typing import Optional
from datetime import datetime

from packet_generator import PacketType
from packet_utils import PacketUtils
from packet_generator import PacketGenerator


from logger_util import setup_logger
logger: Logger = setup_logger('PacketHandler', 'packet_handler.log')

class PacketHandler:
    '''
    This class handles the incoming packets, decodes them,
    and calls appropriate methods to handle different types of packets.
    '''
    
    def __init__(self, packet_generator: PacketGenerator) -> None:
        '''
        Initialize the packet handler
        '''

        self.packet_generator: PacketGenerator = packet_generator
        self.handlers = {
            PacketType.VALIDATOR_REQUEST: self.handle_validator_request,
            PacketType.VALIDATOR_CONFIRMATION: self.handle_validator_confirmation,
            PacketType.VALIDATOR_STATE: self.handle_validator_state,
            PacketType.VALIDATOR_LIST_REQUEST: self.handle_validator_list_request,
            PacketType.VALIDATOR_LIST_RESPONSE: self.handle_validator_list_response,
            PacketType.LATENCY: self.handle_latency,
            PacketType.JOB_FILE: self.handle_job_file,
            PacketType.PAYOUT_FILE: self.handle_payout_file,
            PacketType.SHUT_UP: self.handle_shut_up,
            PacketType.CONVERGENCE: self.handle_convergence,
            PacketType.SYNC_CO_CHAIN: self.handle_sync_co_chain,
            PacketType.SHARE_RULES: self.handle_share_rules,
            PacketType.JOB_REQUEST: self.handle_job_request,
            PacketType.VALIDATOR_CHANGE_STATE: self.handle_validator_change_state,
            PacketType.REPORT: self.handle_report_packet,
            PacketType.PERCEPTION_UPDATE: self.handle_perception_update_packet,
        }

    def handle_packet(self, packet: bytes) -> Optional[bytes]:
        '''
        Receives a packet, decodes it, and calls the appropriate handler.
        Returns a response packet if needed, otherwise None.
        '''
        try:
            # Extract the first 4 bytes for version and 8 bytes for timestamp (keep this data for later use)
            version_data = struct.unpack('!HBBB', packet[:5])  # 16-bit year, 8-bit month, day, subversion
            timestamp = struct.unpack('!Q', packet[5:13])[0]  # 64-bit timestamp

            # Store version and timestamp for later use (or logging)
            self.version_info = {
                "year": version_data[0],
                "month": version_data[1],
                "day": version_data[2],
                "sub_version": version_data[3],
                "timestamp": timestamp
            }

            # Convert the timestamp to a human-readable format
            human_readable_timestamp: str = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')

            logger.info(f"Packet version: {self.version_info}")
            logger.info(f"Packet timestamp: {human_readable_timestamp}")

            # Now that the version and timestamp are stripped, identify the packet type
            packet_type_value = struct.unpack('!H', packet[13:15])[0]
            packet_type = PacketType(packet_type_value)

            logger.info(f"Received packet of type: {packet_type.name}")

            # Debugging: Print payload in hex format for comparison
            logger.debug(f"Packet payload: {packet[15:].hex()}")

            # Now pass the remainder of the packet (payload) to the handler
            handler = self.handlers.get(packet_type)
            if handler:
                return handler(packet[15:])  # Pass the payload
            else:
                logger.error(f"Unknown packet type: {packet_type}")
                return None
        except Exception as e:
            logger.error(f"Failed to handle packet: {e}")
            return None

    def handle_validator_request(self, packet: bytes) -> Optional[bytes]:
        '''
        Handles an incoming validator request packet and returns a confirmation packet.

        A validator request packet is sent when a validator wishes to join the active pool.
        This method extracts the validator’s public key and responds with a confirmation packet.

        Note: Currently, the public key is logged but not yet added to any internal validator state list.
        '''

        logger.info("Handling Validator Request")

        # Unpack the public key (the packet type has already been stripped)
        try:
            public_key = packet.decode("utf-8")  # The entire payload is the public key
        except Exception as e:
            logger.error(f"Unable to extract the public key. Failed to unpack the packet: {e}")
            return None

        logger.info(f"Validator request from: {public_key}")

        # Generate a response using packet generator
        confirmation_packet: bytes = self.packet_generator.generate_validator_confirmation(position_in_queue=4)
        
        return confirmation_packet

    def handle_validator_confirmation(self, packet: bytes) -> None:
        '''
        This handles the response from the validator request packet.

        This packet is sent in response to a validator request and contains the validator’s
        assigned position in the queue.
        '''

        logger.info("Handling Validator Response")
        
        # Unpack the queue position directly (since the payload is already stripped)
        try:
            queue_position = struct.unpack(">I", packet[:4])[0]  # First 4 bytes of the payload = queue position
            logger.info(f"Validator confirmed in queue position: {queue_position}")
        except Exception as e:
            logger.error(f"Failed to unpack the packet: {e}")

    def handle_validator_state(self, packet: bytes) -> None:
        '''
        Handles validator state packet
        '''
        logger.info("Handling Validator State")
        # Unpack and log the validator state
        state = packet[2:].decode("utf-8")
        logger.info(f"Validator state is: {state}")
        ...

    def handle_validator_list_request(self, packet: bytes) -> None:
        '''
        Handles a validator list request packet.

        This packet is used to retrieve the current list of validators in the pool.
        The payload contains two parameters:
        - `include_hash` (1 byte): If 1, return the hash of the validator list; if 0, return the full list
        - `slice_index` (4 bytes): Used to paginate or split responses if the list is large

        This method allows validators to sync their view of the network without always attaching the full list to every confirmation packet.
        '''
        
        logger.info("Handling Validator List Request")
        # Unpack modifiers
        include_hash, slice_index = struct.unpack(">BI", packet[2:7])
        logger.info(f"Validator List Request: Include Hash: {include_hash}, Slice Index: {slice_index}")
        ...

    def handle_validator_list_response(self, packet: bytes, slice_index: Optional[int] = None) -> None:
        '''
        Handles validator list response packet

        This packet includes either a full or partial list of validators, depending on
        what was requested (via slice index). The payload is expected to be a
        UTF-8 encoded comma-separated list of public keys, beginning at the requested offset.
        '''

        logger.info("Handling Validator List Response")
        # Extract the list of validators from the packet
        validators_data = packet[2:]
        validators_data = packet.decode("utf-8")
        validators = validators_data.split(",")

        if slice_index is not None:
            logger.info(f"Received validator slice at index {slice_index}: {validators}")
        else:
            logger.info(f"Received full validator list: {validators}")

        ...

    def handle_latency(self, packet: bytes) -> None:
        '''
        Handles latency packet
        '''

        logger.info("Handling Latency Packet")
        # Extract latency counter and perform latency-related operations
        latency_counter = struct.unpack(">I", packet[2:6])[0]
        logger.info(f"Latency Counter: {latency_counter}")
        ...

    def handle_job_file(self, packet: bytes) -> None:
        '''
        Handles job file packet

        This packet contains job entries sent by clients (or other validators) and must be
        unpacked, validated, and added to the active job pool.

        Job files are a core part of UndChain — they are shared across validators,
        stored temporarily in RAM, and ultimately hashed when a block is finalized.
        '''

        logger.info("Handling Job File")
        # Unpack job file data
        job_data = packet[2:]
        logger.info(f"Job File Data: {job_data.decode('utf-8')}")
        ...

    def handle_payout_file(self, packet: bytes) -> None:
        '''
        Handles payout file packet
        '''
        logger.info("Handling Payout File")
        # Unpack payout file data
        payout_data = packet[2:]
        logger.info(f"Payout File Data: {payout_data.decode('utf-8')}")
        ...

    def handle_shut_up(self, packet: bytes) -> None:
        '''
        Handles shut-up packet

        This packet is sent to temporarily suppress communication from another validator
        or user that is overloading the network with excessive requests.

        Upon receipt, the sending party should enter a cooldown period and
        reduce or pause outbound traffic to the issuing validator.
        '''

        logger.info("Handling Shut-Up Packet")
        # Perform logic to pause communication or reduce traffic load
        ...

    def handle_convergence(self, packet: bytes) -> None:
        '''
        Handles convergence packet

        The Convergence is the process of collapsing the current blockchain state into a
        new genesis block. This is done by hashing the full ledger and storing the
        previous state via UndChain's network storage protocol.

        The convergence mechanism allows UndChain to:
        - Reduce ledger bloat and speed up node bootstrapping
        - Transition between different hashing or encryption algorithms
        '''

        logger.info("Handling Convergence Packet")
        # Extract convergence details
        convergence_time = struct.unpack(">I", packet[2:6])[0]
        logger.info(f"Convergence Time: {convergence_time}")
        ...

    def handle_sync_co_chain(self, packet: bytes) -> None:
        '''
        Handles sync co-chain packet

        This packet is sent by a validator that is joining an existing co-chain
        and needs to synchronize its internal state. The payload contains the co-chain ID.

        Upon receiving this request, the validator should respond with:
        - The current active validator list
        - The shared job file
        - The Run Rules file
        - The current payout file
        - The blockchain
        '''

        logger.info("Handling Sync Co-Chain Packet")
        # Unpack and process the sync co-chain data
        co_chain_id = packet[2:].decode("utf-8")
        logger.info(f"Sync Co-Chain ID: {co_chain_id}")
        ...

    def handle_share_rules(self, packet: bytes) -> None:
        '''
        Handles share rules packet
        '''
        logger.info("Handling Share Rules Packet")
        # Process rule sharing
        rule_version = packet[2:].decode("utf-8")
        logger.info(f"Share Rules version: {rule_version}")
        ...

    def handle_job_request(self, packet: bytes) -> None:
        '''
        Handles job request packet

        This packet is sent by a client (or any user) to submit a request for utility
        services (e.g., storage, compute, access). Once received, the job is validated
        and added to the shared job file, which is visible to eligible partners.

        Partners will scan the job file and respond to requests that match their
        capabilities and availability.
        '''

        logger.info("Handling Job Request")
        job_data = packet[2:].decode("utf-8")
        logger.info(f"Job Request Data: {job_data}")
        ...

    def handle_validator_change_state(self, packet: bytes) -> None:
        '''
        Handles validator change state packet

        This packet notifies other active validators that a given validator has
        changed its operational state. This may include transitions such as:

        - `PENDING` → `ACTIVE`
        - `ACTIVE` → `PASSIVE` (stepping down)
        - `DISCOVERY` → `SYNC`

        This ensures the network has an up-to-date view of validator availability,
        routing behavior, and participation.
        '''

        logger.info("Handling Validator Change State")
        new_state = packet[2:].decode("utf-8")
        logger.info(f"Validator changed to state: {new_state}")
        ...

    def handle_report_packet(self, packet_data: bytearray) -> None:
        '''
        Handles a report packet, used to log and act on misbehavior across the network.

        This packet is submitted when one user (reporter) believes another user
        (reported) has violated protocol expectations or engaged in disruptive behavior.

        The report is parsed and logged, and will influence the perception score
        of the reported party based on validator consensus or accumulated evidence.
        '''

        reporter = PacketUtils._decode_public_key(packet_data[:64])
        reported = PacketUtils._decode_public_key(packet_data[64:128])
        reason = PacketUtils._decode_string(packet_data[128:])
        
        logger.info(f"Received report from {reporter} about {reported} for reason: {reason}.")

    def handle_perception_update_packet(self, packet_data: bytearray) -> None:
        '''
        Handles a perception update packet.

        This packet contains an updated perception score for a specific user, calculated
        through consensus among active validators. Once processed, this score should
        be shared with partners for persistence in UndChain’s decentralized network storage.
        '''

        user_id = PacketUtils._decode_public_key(packet_data[:64])
        new_score = int.from_bytes(packet_data[64:68], byteorder='big')

        logger.info(f"Updating perception score for user {user_id} to {new_score}.")

    def get_packet_type(self, packet: bytes) -> PacketType:
        '''
        Extracts the packet type from the first two bytes of the packet.

        This helper function is used to determine the appropriate handler for
        an incoming packet based on its type ID. The type is represented as a
        16-bit unsigned integer and mapped to the PacketType enum.
        '''
        
        try:
            pack_type_value = struct.unpack(">H", packet[:2])[0] # First two bytes represent the packet type
            return PacketType(pack_type_value)
        except Exception as e:
            logger.error(f'Failed to extract packet type: {e}')
            raise ValueError(f'Unknown packet type from packet {e}')

# Example use
if __name__ == "__main__":
    packet_generator = PacketGenerator("2024.10.09.1")
    handler = PacketHandler(packet_generator)

    # Simulate generating a VALIDATOR_REQUEST packet using PacketGenerator
    public_key = b"validator_pub_key_12345"
    sample_packet: bytes = packet_generator.generate_validator_request(public_key)
    print(f'Sample Packet: {sample_packet}')

    # Now pass the sample packet to the PacketHandler for processing
    return_packet = handler.handle_packet(sample_packet)
    print(f"Generated return packet: {return_packet}")

    if return_packet:
        return_packet = handler.handle_packet(return_packet)

        print(f"Interpreted confirmation packet: {return_packet}")
