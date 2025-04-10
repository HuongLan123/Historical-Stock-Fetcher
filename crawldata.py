from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Khởi động trình duyệt
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Chạy ẩn trình duyệt
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Truy cập trang web
url = "https://vcbs.com.vn/trung-tam-phan-tich/lich-su-giao-dich?stock_symbol=VCB"
driver.get(url)
time.sleep(5)  # Chờ trang tải

all_data = []  # Lưu toàn bộ dữ liệu từ nhiều trang
page = 0
while True:
    print("Đang thu thập dữ liệu từ trang hiện tại...")

    # Tìm hàng tiêu đề
    header_rows = driver.find_elements(By.CSS_SELECTOR, "table thead tr")
    if len(header_rows) >= 2:
        headers = [
        "Ngày", "Giá điều chỉnh", "Giá đóng cửa", "Thay đổi",
        "Giao dịch khớp lệnh_KL", "Giao dịch khớp lệnh_GT",
        "Giao dịch thoả thuận_KL", "Giao dịch thoả thuận_GT",
        "Giá mở cửa", "Giá cao nhất", "Giá thấp nhất"
    ] # Cập nhật headers theo sub_headers sau khi xử lý
    else:
        headers = [th.text.strip() for th in header_rows[0].find_elements(By.TAG_NAME, "th")]

    print(f"Headers: {headers}")

    # Tìm tất cả hàng dữ liệu trong bảng
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    data = []
    count = 0

    for index, row in enumerate(rows):
        cols = row.find_elements(By.TAG_NAME, "td")
        row_data = [col.text.strip() for col in cols]
        try:
            # Kiểm tra số lượng cột có khớp không, nếu không thì bỏ qua hàng
            if len(row_data) != len(headers):
                raise ValueError("Số lượng cột không khớp với headers")

            print(f"Row data: {row_data}")  # Debug: In dữ liệu từng hàng
            data.append(row_data)
            count += 1
        except Exception as e:
            print(f"Bỏ qua hàng do lỗi: {e}")
            continue

    # Chuyển dữ liệu thành DataFrame và lưu vào danh sách
    try:
        df = pd.DataFrame(data, columns=headers)
        all_data.append(df)
    except Exception as e:
        print(f"Lỗi khi tạo DataFrame: {e}")

    # **Tìm và nhấn vào nút "Next" để chuyển trang**
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next page']")
        if "disabled" in next_button.get_attribute("class"):
            break  # Dừng nếu không còn trang tiếp theo
        next_button.click()
        time.sleep(5)  # Chờ trang tải
        page += 1
    except:
        break  # Dừng vòng lặp nếu không tìm thấy nút chuyển trang
# Gộp tất cả DataFrame từ các trang
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    print(final_df)
# Lưu dữ liệu vào file Excel
output_file = "data_vcbs.xlsx"
try:
    df.to_excel(output_file, index=False)
    print(f"Dữ liệu đã được lưu vào {output_file}")
except Exception as e:
    print(f"Lỗi khi lưu file Excel: {e}")
# Đóng trình duyệt
driver.quit()