import cv2
import numpy as np
from PIL import Image
import io

class F5SteganographyService:
    def __init__(self):
        self.Q = np.array(
            [
                [16, 11, 10, 16, 24, 40, 51, 61],
                [12, 12, 14, 19, 26, 58, 60, 55],
                [14, 13, 16, 24, 40, 57, 69, 56],
                [14, 17, 22, 29, 51, 87, 80, 62],
                [18, 22, 37, 56, 68, 109, 103, 77],
                [24, 35, 55, 64, 81, 104, 113, 92],
                [49, 64, 78, 87, 103, 121, 120, 101],
                [72, 92, 95, 98, 112, 100, 103, 99],
            ]
        )
        self.M = np.array(
            [
                [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
                [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
                [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            ]
        )

    def hideSecretMessageInImage(self, image_bytes: bytes, secret_message: str,formatOutupt: str) -> bytes:
        print(f"secret : {secret_message} , format {formatOutupt}")
        image = self._imageBytesToImageImage(image_bytes)
        print("imagge  ")
        stego_image = self._encode(image, secret_message)
        return self._imageImageTobytes(stego_image,formatOutupt)

    def extractSecretMessageFromImage(self, image_bytes: bytes) -> str:
        image = self._imageBytesToImageImage(image_bytes)
        secret_message = self._decode(image)
        return secret_message
    
    def _imageImageTobytes(self, image: Image.Image, formatOutupt: str) -> bytes:
        out_stream = io.BytesIO()
        formatOutupt = formatOutupt.lower()
        if formatOutupt == "jpg" or formatOutupt == "jpeg":
            image.save(out_stream, quality=100, subsampling=0,format=formatOutupt)
        else:
            image.save(out_stream,format=formatOutupt)
        return out_stream.getvalue()

    def _imageBytesToImageImage(self,image_bytes: bytes)->Image.Image:
        image_stream = io.BytesIO(image_bytes)
        image = Image.open(image_stream).convert("RGB")
        return image

    
    def _dct(self, before: np.ndarray, block_y: int, block_x: int) -> np.ndarray:
        # Calcul de la DCT et la quantification sur chaque matrice 8x8 de l’image
        for i in range(block_y):
            for j in range(block_x):
                start_y, end_y = 8 * i, 8 * (i + 1)
                start_x, end_x = 8 * j, 8 * (j + 1)
                block = before[start_y:end_y, start_x:end_x]
                dct_block = cv2.dct(block)
                dct_block = np.around(dct_block)
                quant_block = np.divide(dct_block, self.Q)
                before[start_y:end_y, start_x:end_x] = np.around(quant_block)
        return before

    def _idct(self, before: np.ndarray, block_y: int, block_x: int) -> np.ndarray:
        # Déquantification et l’IDCT sur chaque matrice 8x8 de l’image.
        for i in range(block_y):
            for j in range(block_x):
              start_y, end_y = 8 * i, 8 * (i + 1)
              start_x, end_x = 8 * j, 8 * (j + 1)
              block = before[start_y:end_y, start_x:end_x]
              dequant_block = np.multiply(block, self.Q)
              idct_block = cv2.idct(dequant_block)
              before[start_y:end_y, start_x:end_x] = idct_block
        return before
        

    def _encode(self, image_original: Image.Image, secret_message: str) -> Image.Image:
        img = np.array(image_original)
        img1 = img[:, :, 1]
        h, w = img1.shape
        img1 = img1.astype(np.float32)
        d = img1
        block_y = h // 8
        block_x = w // 8
        d = self._dct(d, block_y, block_x)
        byte_s = secret_message.encode("utf-8")
        hex_bin = byte_s.hex()
        oct_bin = oct(int(hex_bin, 16))
        binary_bin = bin(int(oct_bin, 8))[2:].zfill(len(hex_bin) * 4)
        lenth_bin = bin(len(binary_bin))[2:].zfill(12)
        binary_bin = lenth_bin + binary_bin
        data_lenth = len(binary_bin)
        stego = d
        num = 0
        a = np.zeros((15, 1))
        k = 0
        sit = np.zeros((15, 2))
        for i in range(block_y * 8):
            for j in range(block_x * 8):
                if (d[i, j] > 0 and (d[i, j] % 2) == 1) or (
                    d[i, j] < 0 and (d[i, j] % 2) == 0
                ):
                    a[k] = 1
                    sit[k][0] = i
                    sit[k][1] = j
                    k = k + 1
                elif (d[i, j] < 0 and (d[i, j] % 2) == 1) or (
                    d[i, j] > 0 and (d[i, j] % 2) == 0
                ):
                    a[k] = 0
                    sit[k][0] = i
                    sit[k][1] = j
                    k = k + 1
                if k >= 15:
                    data_bit = np.zeros((4, 1))
                    data_bit[0][0] = binary_bin[num]
                    num = num + 1
                    data_bit[1][0] = binary_bin[num]
                    num = num + 1
                    data_bit[2][0] = binary_bin[num]
                    num = num + 1
                    data_bit[3][0] = binary_bin[num]
                    temp = np.dot(self.M, a)
                    temp = temp % 2
                    ntemp = np.logical_xor(data_bit, temp)
                    n = (
                        ntemp[0][0] * 8
                        + ntemp[1][0] * 4
                        + ntemp[2][0] * 2
                        + ntemp[3][0]
                        - 1
                    )
                    if n >= 0:
                        if d[int(sit[n][0])][int(sit[n][1])] < 0:
                            stego[int(sit[n][0])][int(sit[n][1])] = (
                                d[int(sit[n][0])][int(sit[n][1])] + 1
                            )
                        elif d[int(sit[n][0])][int(sit[n][1])] > 0:
                            stego[int(sit[n][0])][int(sit[n][1])] = (
                                d[int(sit[n][0])][int(sit[n][1])] - 1
                            )
                        if stego[int(sit[n][0])][int(sit[n][1])] == 0:
                            k = k - 1
                            if n < 14:
                                sit[n:k, :] = sit[n + 1 : k + 1, :]
                                a[n:k] = a[n + 1 : k + 1]
                            if n == 14:
                                ...
                            num = num - 3
                            continue
                    num = num + 1
                    k = 0
                if num >= data_lenth:
                    break
            if num >= data_lenth:
                break
        stego = self._idct(stego, block_y, block_x)
        for i in range(h):
            for j in range(w):
                if stego[i][j] > 255:
                    stego[i][j] = 255
                if stego[i][j] < 0:
                    stego[i][j] = 0
        stego = np.round(stego)
        stego = np.uint8(stego)
        img[:, :, 1] = stego
        new_img = Image.fromarray(np.uint8(img))
        return new_img

    def _decode(self, image_original: Image.Image) -> str:
        img = np.array(image_original)
        img1 = img[:, :, 1]
        data_lenth = 100
        extract = ""
        h, w = img1.shape
        d = np.zeros(img1.shape)
        block_y = h // 8
        block_x = w // 8
        img1 = img1.astype(np.float32)
        d = self._dct(img1, block_y, block_x)
        num = 0
        a = np.zeros((15, 1))
        k = 0
        for i in range(block_y * 8):
            for j in range(block_x * 8):
                if (d[i, j] > 0 and (d[i, j] % 2) == 1) or (
                    d[i, j] < 0 and (d[i, j] % 2) == 0
                ):
                    a[k] = 1
                    k = k + 1
                elif (d[i, j] < 0 and (d[i, j] % 2) == 1) or (
                    d[i, j] > 0 and (d[i, j] % 2) == 0
                ):
                    a[k] = 0
                    k = k + 1
                if k >= 15:
                    temp = np.dot(self.M, a)
                    temp = temp % 2
                    extract += str(int(temp[0][0]))
                    extract += str(int(temp[1][0]))
                    extract += str(int(temp[2][0]))
                    extract += str(int(temp[3][0]))
                    num = num + 4
                    if num == 12:
                        data_lenth = int(extract[:12], 2) + 12
                    k = 0
                if num >= data_lenth:
                    break
            if num >= data_lenth:
                break
        val = hex(int(extract[12:], 2))[2:] 
        val = val.zfill(len(val) + len(val) % 2) 
        message =bytes.fromhex(val).decode('utf-8', errors='ignore')
        print(message)
        return message

F5_stegano = F5SteganographyService()