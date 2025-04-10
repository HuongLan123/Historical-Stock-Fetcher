from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Cấu hình Chrome headless
options = webdriver.ChromeOptions()
options.add_argument("--headless")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Mở URL
url = "https://vcbs.com.vn/trung-tam-phan-tich/lich-su-giao-dich?stock_symbol=VCB"
driver.get(url)
time.sleep(5)

all_data = []
page = 0
expected_columns = 11  # Số lượng cột dữ liệu

while True:
    print(f"Đang thu thập dữ liệu trang {page + 1}...")

    # Cập nhật tiêu đề chuẩn (cố định theo ảnh)
    headers = [
        "Ngày", "Giá điều chỉnh", "Giá đóng cửa", "Thay đổi",
        "Giao dịch khớp lệnh_KL", "Giao dịch khớp lệnh_GT",
        "Giao dịch thỏa thuận_KL", "Giao dịch thỏa thuận_GT",
        "Giá mở cửa", "Giá cao nhất", "Giá thấp nhất"
    ]

    # Lấy dữ liệu từng hàng trong bảng
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    data = []

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        row_data = [col.text.strip() for col in cols]

        if len(row_data) != expected_columns:
            print(f"⚠️ Bỏ qua hàng có {len(row_data)} cột: {row_data}")
            continue

        data.append(row_data)

    # Thêm vào danh sách nếu có dữ liệu
    try:
        df = pd.DataFrame(data, columns=headers)
        all_data.append(df)
    except Exception as e:
        print(f"Lỗi tạo DataFrame: {e}")

    # Tìm nút "Next page" để chuyển trang
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next page']")
        if "disabled" in next_button.get_attribute("class"):
            break  # Hết trang
        next_button.click()
        time.sleep(5)
        page += 1
    except:
        break  # Không thấy nút "Next"

# Gộp dữ liệu và lưu Excel
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    print(final_df.head())  # In thử vài dòng

    output_file = "data_vcbs.xlsx"
    try:
        final_df.to_excel(output_file, index=False)
        print(f"✅ Đã lưu dữ liệu vào {output_file}")
    except Exception as e:
        print(f"❌ Lỗi khi lưu Excel: {e}")
else:
    print("❌ Không thu thập được dữ liệu nào.")

# Đóng trình duyệt
driver.quit()
