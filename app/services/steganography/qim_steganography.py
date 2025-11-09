from PIL import Image
import io
import numpy as np

class QimSteganographieService:

    @staticmethod
    def bytes_to_bits(data_bytes):
        bits = []
        for b in data_bytes:
            for i in range(8)[::-1]:
                bits.append((b >> i) & 1)
        return bits

    @staticmethod
    def bits_to_bytes(bits):
        if len(bits) % 8 != 0:
            bits += [0] * (8 - len(bits) % 8)
        out = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for bit in bits[i:i+8]:
                byte = (byte << 1) | bit
            out.append(byte)
        return bytes(out)

    @staticmethod
    def qim_quantize_scalar(x, b, delta):
        shift = (b * delta) / 2.0
        q = delta * round((x - shift) / delta) + shift
        return q

    @staticmethod
    def embed_bits_in_array(flat_arr, bits, delta):
        if len(bits) > flat_arr.size:
            raise ValueError("Pas assez de capacité pour écrire tous les bits.")
        for i, bit in enumerate(bits):
            x = float(flat_arr[i])
            q = QimSteganographieService.qim_quantize_scalar(x, bit, delta)
            flat_arr[i] = np.clip(round(q), 0, 255)
        return flat_arr

    @staticmethod
    def extract_bits_from_array(flat_arr, n_bits, delta):
        if n_bits > flat_arr.size:
            raise ValueError("Demande d'extraction > capacité de l'image.")
        bits = []
        for i in range(n_bits):
            x = float(flat_arr[i])
            q0 = QimSteganographieService.qim_quantize_scalar(x, 0, delta)
            q1 = QimSteganographieService.qim_quantize_scalar(x, 1, delta)
            bit = 0 if abs(x - q0) <= abs(x - q1) else 1
            bits.append(bit)
        return bits

    @staticmethod
    def embed_message_rgb(img_rgb: Image.Image, message: str, delta=16):
        r, g, b = img_rgb.split()
        b_arr = np.array(b, dtype=np.float32)
        flat_b = b_arr.flatten()

        msg_bytes = message.encode('utf-8')
        msg_len = len(msg_bytes)
        header = msg_len.to_bytes(4, 'big')
        payload = header + msg_bytes
        bits = QimSteganographieService.bytes_to_bits(payload)

        if len(bits) > flat_b.size:
            raise ValueError(f"Capacité insuffisante: {len(bits)} bits pour {flat_b.size} pixels.")

        flat_b = QimSteganographieService.embed_bits_in_array(flat_b, bits, delta)
        b_stego = flat_b.reshape(b_arr.shape).astype(np.uint8)

        stego_img = Image.merge("RGB", (r, g, Image.fromarray(b_stego)))
        return stego_img

    @staticmethod
    def extract_message_rgb(img_rgb: Image.Image, delta=16):
        r, g, b = img_rgb.split()
        b_arr = np.array(b, dtype=np.float32)
        flat_b = b_arr.flatten()

        header_bits = QimSteganographieService.extract_bits_from_array(flat_b, 32, delta)
        header_bytes = QimSteganographieService.bits_to_bytes(header_bits)
        msg_len = int.from_bytes(header_bytes, 'big')

        n_bits_total = (4 + msg_len) * 8
        payload_bits = QimSteganographieService.extract_bits_from_array(flat_b, n_bits_total, delta)
        payload_bytes = QimSteganographieService.bits_to_bytes(payload_bits)
        msg_bytes = payload_bytes[4:4+msg_len]
        try:
            return msg_bytes.decode('utf-8')
        except Exception:
            return msg_bytes.decode('utf-8', errors='replace')

    @staticmethod
    def hideSecretMessageInImage(image_bytes: bytes, secret_message: str, format_output: str = "png", delta: float = 4) -> bytes:
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        except Exception as e:
            raise ValueError(f"Erreur lecture image: {e}")

        stego_img = QimSteganographieService.embed_message_rgb(img, secret_message, delta=delta)

        output_bytes_io = io.BytesIO()
        stego_img.save(output_bytes_io, format=format_output.upper())
        return output_bytes_io.getvalue()

    @staticmethod
    def extractSecretMessageFromImage(image_bytes: bytes, delta: float = 4) -> str:
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        except Exception as e:
            raise ValueError(f"Erreur lecture image: {e}")

        return QimSteganographieService.extract_message_rgb(img, delta=delta)


qimSteganographieService =  QimSteganographieService()