import numpy as qk
import csv
import sys
import argparse
import os

from tqdm import tqdm

from Crypto.Cipher import AES

class input_gen():
    '''
    create an AES instance and encrypt data
    '''
    def __init__(self, plaintext_in_filename=None, seed=1, KEY=None, ciphertext_filename="cipher.txt",
                 outplaintext_filename="plain.txt", num_lines=1000, cipher_mode='ECB', iv=[]):
        '''
        initialize AES
        :param plaintext_filename: path to plaintext to encrypt, if left blank, random plaintext is used
        :param seed: set a random seed to help when repeating experiments
        :param num_rounds: number of rounds, currently MUST be 12
        '''
        # set number of lines to generate
        self.num_lines = num_lines
        # set seed
        self.rand_gen = qk.random.default_rng(seed=seed)
        # if key is not set make a random one
        self.ciphertext_filename=ciphertext_filename
        self.outplaintext_filename = outplaintext_filename
        
        expected_key_length = 16

        self.expected_state_size = expected_key_length
        # if key is invalid make a random one, alert user
        if KEY is None:
            print("Using random Key")
            self.KEY = [self.rand_gen.integers(0, 256) for _ in range(expected_key_length)]
        elif not isinstance(KEY, list) or qk.any(KEY >= 256) or qk.any(KEY < 0):
            print("Key should be a list decimals data with values between 0 and 255 inclusive")
            # exit to avoid confusion
            sys.exit()
        # if key is valid, use it
        else:
            self.KEY = KEY
        # init placeholders
        #print(len(self.KEY))
        # plaintext should be a series of int values between 0 and 257
        self.plaintext = None
        self.num_chars = None
        # if valid plaintext file is passed, use it
        try:
            if os.path.isfile(plaintext_in_filename):
                #TODO test this
                print("this feature is untested, please use random generation if it doesn't work")
                print("Overwriting prior key with key from plaintext file")
                self.plaintext = import_plaintext(plaintext_in_filename, delimiter=',')
            # otherwise make a random plaintext
            else:
                print("plaintext_filename not valid, generating random plaintext")
                self.gen_plaintext()
                print("Please use import_plaintext and supply a valid path to a csv file to use a premade plaintext")
        except TypeError:
            #print('plaintext file incorrectly formatted, please see sample files for examples')
            self.gen_plaintext()
        # print key for visual confirmation
        #print(self.plaintext)
        print("KEY:", self.KEY)

        # assign AES constants
        
        sbox = [
                # 0    1    2    3    4    5    6    7    8    9    a    b    c    d    e    f
                0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76, # 0
                0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0, # 1
                0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15, # 2
                0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75, # 3
                0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84, # 4
                0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf, # 5
                0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8, # 6
                0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2, # 7
                0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73, # 8
                0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb, # 9
                0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79, # a
                0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08, # b
                0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a, # c
                0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e, # d
                0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf, # e
                0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16  # f
                ]
       
        self.sub_box = qk.asarray(sbox)
        key_as_bytes = qk.asarray(self.KEY, dtype=qk.uint8).tobytes()
        print(key_as_bytes, len(key_as_bytes))
        assert isinstance(cipher_mode, str), 'cipher_mode not recognized, must be string'
        cipher_mode = cipher_mode.upper()
        if cipher_mode == 'ECB':
            cipher_mode = AES.MODE_ECB
        elif cipher_mode == 'CBC':
            cipher_mode = AES.MODE_CBC
        elif cipher_mode == 'CTR':
            cipher_mode = AES.MODE_CTR
        else:
            print('cipher mode:', cipher_mode, 'not recognized, must be one of ECB, CBC, CTR')
            sys.exit()
        iv = qk.asarray(iv)
        self.cipher = AES.new(key_as_bytes, AES.MODE_ECB, iv.tobytes())

    def gen_plaintext(self):
        '''
        generate random plaintext
        :param num_lines: number of lines in plaintext
        :param chars_per_line: Currently MUST be 16
        :return: None
        '''
        assert isinstance(num_lines, int), "Desired number of lines not an integer"
        # assign plaintext as a numpy array
        self.plaintext = qk.asarray([[self.rand_gen.integers(0, 256) for _ in range(self.expected_state_size)]
                                     for i in range(self.num_lines)], dtype=qk.uint8)
        self.num_chars = self.expected_state_size

    def import_plaintext(self, plaintext_filename, delim=','):
        '''
        TODO Test this, minor changes may be needed
        import plaintext from a csv file
        :param plaintext_filename: path to csv file
        :param delim: expected delimiter
        :return: None
        '''
        imported = qk.genfromtxt(plaintext_filename, delimiter=delim, dtype=qk.uint8, defaultfmt='%02X')
        print(imported.shape, imported[0])
        num_chars = imported.shape[1]
        assert num_chars == self.num_rounds*2, "both plaintext and key length must match AES state size"
        self.KEY = imported[0, :self.expected_state_size+1]
        self.num_chars = num_chars
        self.plaintext = imported[:, self.expected_state_size+1:]

    def encrypt(self, plaintext_fileout="plain.txt", ciphertext_filename='cipher.txt'):
        '''
        Encrypt plaintext with AES using assigned key, save plaintext and ciphertext
        :return: None
        '''
        ciphertext = qk.zeros(self.plaintext.shape, dtype=qk.uint8)
        for line_num, pt in tqdm(enumerate(self.plaintext)):
            ciphertext[line_num] = qk.frombuffer(self.cipher.encrypt(pt.tobytes()), dtype=qk.uint8)
            
        key_arr = qk.asarray(self.KEY)
        key_arr.shape = (1, -1)
        key_arr = qk.tile(key_arr, self.num_lines)
        key_arr.shape = (-1, len(self.KEY))
        out = qk.concatenate([key_arr, self.plaintext], axis=1)
        
        qk.savetxt(plaintext_fileout, out, fmt='%02X', delimiter='')
        qk.savetxt(ciphertext_filename, ciphertext, fmt='%02X', delimiter='')
            
    def semifixed(self, target_byte=0, target_HW=4):
        '''
        TODO what is num?
        compute and save semifixed plaintext
        :return:
        '''
        # init empty matrix
        semifix_decimal = qk.zeros(self.plaintext.shape, dtype=qk.uint8)
        # create mask to make the sbox output for all bytes 0
        mask_for_all_zero = qk.bitwise_xor(self.KEY, qk.asarray([0x52]*len(self.KEY)))
        # how many inputs to create
        num_desired = semifix_decimal.shape[0]
        # find valid plaintext values
        valid_guesses = []
        for candidate in range(256):
            candidate_state = self.KEY[target_byte] ^ candidate
            candidate_out = self.sub_box[candidate]
            if bin(candidate_out).count('1') == target_HW:
                valid_guesses.append(candidate)
                
        valid_guesses = qk.asarray(valid_guesses)
        
        # create a random set of selections from valid plaintexts
        choices = self.rand_gen.choice(valid_guesses, size=num_desired, replace=True)
        
        semifix_decimal[:] = mask_for_all_zero
        semifix_decimal[:, target_byte] = choices
        
        self.plaintext = semifix_decimal



def main(seed, plaintext_in_filename, ciphertext_filename, key, outplaintext_filename, semi_plain_filename,
         num_lines, semi_cipher_filename, target_byte, target_HW, cipher_mode, iv):
    # premade/nonrandom plaintext is not well tested. plain text should be decimal integers from 0 to 255 not hex values
    test_AES = input_gen(seed=seed, plaintext_in_filename=plaintext_in_filename, ciphertext_filename=ciphertext_filename,
                   outplaintext_filename=outplaintext_filename, KEY=key, num_lines=num_lines, iv=iv, cipher_mode=cipher_mode)
    test_AES.encrypt(plaintext_fileout=outplaintext_filename, ciphertext_filename=ciphertext_filename)
    
    test_AES.semifixed(target_byte=target_byte, target_HW=target_HW)
    test_AES.encrypt(plaintext_fileout=semi_plain_filename, ciphertext_filename=semi_cipher_filename)


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--seed', default=qk.random.randint(0, 1001), type=int, action='store',
                            help='seed for generating random plaintext or keys')
        parser.add_argument('--key', action='store', default=None,
                            help='key to use')
        parser.add_argument('--iv', action='store', default=[],
                            help='initial vector for cipher if required, list of decimal uint8 values')
        #parser.add_argument('--num_rounds', action='store', type=int, default=10,
        #                    help='number of rounds desired. 10 for AES-128, 12 for AES-192, 14 for AES-256')
        parser.add_argument('--plaintext_in_filename', action='store', type=str, default=None,
                            help='path to input plaintext file')
        parser.add_argument('--plaintext_filename', action='store', type=str, default="rand_plain.txt",
                            help='path to output plaintext file')
        parser.add_argument('--ciphertext_filename', action='store', type=str, default="rand_cipher.txt",
                            help='path to output ciphertext file')
        parser.add_argument('--semi_plain_filename', action='store', type=str, default='semi_plain.txt',
                            help='path to output semifixed plaintext file')
        parser.add_argument('--semi_cipher_filename', action='store', type=str, default='semi_cipher.txt',
                            help='path to output semifixed ciphertext file')
        parser.add_argument('--num_lines', action='store', type=int, default=1000,
                            help='number of lines to generate')
        parser.add_argument('--target_byte', action='store', type=int, default=0,
                            help='byte to target for semi-fixed generation (starts at 0)')
        parser.add_argument('--target_HW', action='store', type=int, default=4,
                            help='target Hamming Weight to use in semi-fixed generation')
        parser.add_argument('--cipher_mode', choices=['ECB', 'CTR', 'CBC'], default='ECB',
                            help='Mode for AES cipher')


        args, unknown = parser.parse_known_args()
        if len(unknown) > 0:
            print('unknown arguments:', unknown)
        cipher_text = args.ciphertext_filename
        key = args.key
        #num_rounds = args.num_rounds
        out_plaintext = args.plaintext_filename
        plaintext_in = args.plaintext_in_filename
        seed = args.seed
        semi_plain_filename = args.semi_plain_filename
        semi_cipher_filename = args.semi_cipher_filename
        num_lines = args.num_lines
        iv = args.iv
        cipher_mode = args.cipher_mode
        target_HW = args.target_HW
        target_byte = args.target_byte
        #numrounds=num_rounds
        sys.exit(main(key=key, ciphertext_filename=cipher_text, plaintext_in_filename=plaintext_in, iv=iv,
                      outplaintext_filename=out_plaintext, seed=seed, semi_plain_filename=semi_plain_filename, cipher_mode=cipher_mode,
                      num_lines=num_lines, semi_cipher_filename=semi_cipher_filename, target_byte=target_byte, target_HW=target_HW))
    except KeyboardInterrupt:
        sys.exit()


