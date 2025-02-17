import segno
import base64
from io import BytesIO


def generate_tax_qr(order, items, time):
    # Формируем информацию для QR-кода
    info = f"Списание №{order.id}\n\n"

    total_cost = 0
    for item in items:
        total_cost += item.paid
        info += f"\tПо {item.code.name} ({item.code.decryption}) выплачено {item.paid}р.\n"

    info += f"Общая выплаченная сумма = {total_cost}р.\n"
    info += f"Сумма вычета = {order.summ}р.\n\n"

    completed_at_str = time.strftime('%Y-%m-%d %H:%M:%S')
    info += f"Дата и время списания: {completed_at_str}"

    # Генерация QR-кода
    qr = segno.make(info)
    buffer = BytesIO()
    qr.save(buffer, kind='png')
    buffer.seek(0)

    # Конвертация изображения в base64
    qr_image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return qr_image_base64