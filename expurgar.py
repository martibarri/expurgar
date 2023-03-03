import argparse


def input_choice(msg):
    choice = input(f"{msg}").lower()
    while choice not in ["y", "n", ""]:
        print('please input "y/n"')
        choice = input(f"{msg}").lower()
    return choice


class Expurgar:
    def __init__(self, filename, chain_len):
        self.filename = filename
        self.file_length = None
        self.chain_len = chain_len
        self.chain_id = 0
        self.chains = []
        # certificate extraction
        self.begin_cert = b"-----BEGIN CERTIFICATE-----"
        self.end_cert = b"-----END CERTIFICATE-----"
        self.saving_cert = False
        self.current_cert = b""
        self.cert_id = 0
        self.certs = []

    def build_chain(self, byte: bytes, count: int, start: int):
        chain = {
            "chain_id": self.chain_id,
            "byte": byte,
            "chain_start": start,
            "chain_count": count,
        }
        self.chain_id += 1
        print(chain)
        self.chains.append(chain)

    def build_cert(self, pos: int):
        if self.saving_cert:
            cert = {
                "cert_id": self.cert_id,
                "cert_begin": pos,
                "cert_end": None,
            }
            self.certs.append(cert)
            print(cert)
        else:
            self.certs[-1]["cert_end"] = pos
            self.cert_id += 1
            print(self.certs[-1])

    def file_analyzer(self):
        f = open(self.filename, "rb", newline=None)
        last_byte = b""
        pos = 0
        count = 1
        while byte := f.read(1):
            pos += 1
            if byte == last_byte:
                count += 1
            else:
                if count > self.chain_len:
                    # save chain
                    self.build_chain(last_byte, count, (pos - 1) - count)
                # start over
                count = 1
            self.cert_analyzer(byte, pos)
            last_byte = byte
        # save last chain
        if count > self.chain_len:
            self.build_chain(last_byte, count, pos - count)
        # save last cert
        if self.saving_cert:
            self.build_cert()  # TODO
        self.file_length = pos
        print(f"Total file bytes: {self.file_length}")
        f.close()

    def cert_analyzer(self, byte: bytes, pos: int):
        # cert extract
        if self.saving_cert:
            if self.end_cert.startswith(self.current_cert + byte):
                self.current_cert += byte
                if self.current_cert == self.end_cert:
                    # end certificate
                    self.saving_cert = False
                    self.current_cert = b""
                    self.build_cert(pos - len(self.end_cert))
            else:
                self.current_cert = b""
        else:
            if self.begin_cert.startswith(self.current_cert + byte):
                self.current_cert += byte
                if self.current_cert == self.begin_cert:
                    # begin certificate
                    self.saving_cert = True
                    self.current_cert = b""
                    self.build_cert(pos - len(self.begin_cert))
            else:
                self.current_cert = b""

    def remove_chain(self, chain_id: int):
        if chain_id >= 0 and (chain_id <= self.chain_id):
            try:
                chain_to_remove = list(
                    filter(lambda x: x.get("chain_id") == chain_id, self.chains)
                )[0]
            except IndexError:
                print("chain not found")
            else:
                print("chain to remove:")
                print(chain_to_remove)
                chain_start = chain_to_remove.get("chain_start")
                chain_count = chain_to_remove.get("chain_count")
                # read file
                f = open(self.filename, "rb", newline=None)
                first_part = f.read(chain_start)
                f.seek(chain_count + chain_start)
                second_part = f.read(self.file_length)  # rest of the file
                f.close()
                # save file
                new_filename = self.filename + ".stripped"
                f = open(new_filename, "wb", newline=None)
                f.write(first_part)
                f.write(second_part)
                f.close()
                print(f"file {new_filename} saved")

    def extract_cert(self, cert_id: int):
        if cert_id >= 0 and (cert_id <= self.cert_id):
            try:
                cert_to_extract = list(
                    filter(lambda x: x.get("cert_id") == cert_id, self.certs)
                )[0]
            except IndexError:
                print("cert not found")
            else:
                print("cert to extract:")
                print(cert_to_extract)
                cert_begin = cert_to_extract.get("cert_begin")
                cert_end = cert_to_extract.get("cert_end")
                # read file
                f = open(self.filename, "rb", newline=None)
                f.seek(cert_begin)
                cert = f.read((cert_end + len(self.end_cert)) - cert_begin)
                f.close()
                # save file
                new_filename = self.filename + ".cert"
                f = open(new_filename, "wb", newline=None)
                f.write(cert)
                f.close()
                print(f"file {new_filename} saved")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, type=str)
    parser.add_argument("-c", "--chain", default=80, type=int)
    args = parser.parse_args()
    expurgar = Expurgar(args.file, args.chain)
    expurgar.file_analyzer()
    if expurgar.chains:
        save_choice = input_choice("remove chain? [y/N] ")
        if save_choice == "y":
            try:
                chain_id = int(input("Enter id: "))
            except ValueError:
                print("Invalid id")
            else:
                expurgar.remove_chain(chain_id)
    if expurgar.certs:
        save_choice = input_choice("extract cert? [y/N] ")
        if save_choice == "y":
            try:
                cert_id = int(input("Enter id: "))
            except ValueError:
                print("Invalid id")
            else:
                expurgar.extract_cert(cert_id)


if __name__ == "__main__":
    main()
