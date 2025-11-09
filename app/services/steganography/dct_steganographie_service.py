import fastapi
import numpy as np
import cv2


class DctSteganographieService:
    def text_to_bits(self, text):
        return [int(b) for b in ''.join(f'{c:08b}' for c in (text + '\0').encode('utf-8'))]

    def bits_to_text(self, bits):
        bits = bits[:-8]
        bytes_list = [bits[i:i + 8] for i in range(0, len(bits), 8)]
        return ''.join(chr(int(''.join(map(str, byte)), 2)) for byte in bytes_list)

    def _embed_dct(self, img, message, strength=35):
        bits = self.text_to_bits(message)
        h, w = img.shape[:2]

        yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        Y = yuv[:, :, 0].astype(np.float32)
        idx = 0

        for i in range(0, h - 8, 8):
            for j in range(0, w - 8, 8):
                if idx >= len(bits):
                    yuv[:, :, 0] = np.clip(np.round(Y), 0, 255).astype(np.uint8)
                    return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

                block = Y[i:i + 8, j:j + 8]
                dct = cv2.dct(block)

                dct[5, 2] = strength if bits[idx] else -strength

                Y[i:i + 8, j:j + 8] = cv2.idct(dct)
                idx += 1

        yuv[:, :, 0] = np.clip(np.round(Y), 0, 255).astype(np.uint8)
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

    def _extract_dct(self, stegano_img, strength=35):
        yuv = cv2.cvtColor(stegano_img, cv2.COLOR_BGR2YUV)
        Y = yuv[:, :, 0].astype(np.float32)
        bits = []

        for i in range(0, Y.shape[0] - 8, 8):
            for j in range(0, Y.shape[1] - 8, 8):
                block = Y[i:i + 8, j:j + 8]
                dct = cv2.dct(block)
                val = dct[5, 2]
                bit = 1 if val > 0 else 0
                bits.append(bit)

                if len(bits) >= 8 and bits[-8:] == [0] * 8:
                    return self.bits_to_text(bits)

        return self.bits_to_text(bits)
    
    def hideSecretMessageInImage(self, image_bytes: bytes, secret_message: str,format_output: str) -> bytes:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        stego_img = self._embed_dct(img, secret_message)
        output_ext = (format_output or "png").lower().lstrip('.')
        ext = f".{output_ext}"
        success, buf = cv2.imencode(ext, stego_img)
        return buf.tobytes()
    
    def extractSecretMessageFromImage(self, image_bytes: bytes):
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return self._extract_dct(img)


dctSteganographieService = DctSteganographieService()
