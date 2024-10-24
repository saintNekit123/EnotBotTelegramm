const jsQR = require('jsqr');
const Jimp = require('jimp');

async function scanQRCode(imagePath) {
    const image = await Jimp.read(imagePath);
    image.resize(1000, Jimp.AUTO); // Увеличиваем ширину до 1000 пикселей
    image.grayscale(); // Преобразуем в оттенки серого

    const { width, height, data } = image.bitmap;

    let qrData = jsQR(data, width, height);

    // Функция для сканирования с вращением изображения
    async function tryRotation(degrees) {
        const rotatedImage = image.clone().rotate(degrees); // Вращаем изображение на заданный угол
        const { width: rotatedWidth, height: rotatedHeight, data: rotatedData } = rotatedImage.bitmap;
        return jsQR(rotatedData, rotatedWidth, rotatedHeight);
    }

    // Если не нашли QR-код, пробуем повернуть изображение
    if (!qrData) {
        const angles = [90, 180, 270]; // Углы для вращения
        for (let angle of angles) {
            qrData = await tryRotation(angle);
            if (qrData) {
                break; // Если нашли QR-код после вращения, выходим из цикла
            }
        }
    }

    if (qrData) {
        return qrData.data; // Возвращаем найденный QR-код
    } else {
        return JSON.stringify({ error: "QR-код не найден." });
    }
}

// Вызываем функцию, если файл запускается напрямую
if (require.main === module) {
    const imagePath = process.argv[2]; // Получаем путь к изображению из аргументов командной строки
    scanQRCode(imagePath).then(result => {
        console.log(result); // Выводим результат в консоль
    });
}

module.exports = { scanQRCode };
