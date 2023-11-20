from PIL import Image
import streamlit as st
import os
import shutil
from zipfile import ZipFile
from pathlib import Path

# Streamlit 页面配置
st.set_page_config(
    page_title="Image Label Viewer", layout="wide", initial_sidebar_state="expanded"
)

# Streamlit 侧边栏
st.sidebar.title("Configuration")

# 文件夹路径
images_folder = st.sidebar.file_uploader("Upload Images Folder", type=["zip"])
labels_folder = st.sidebar.file_uploader("Upload Labels Folder", type=["zip"])
output_folder = st.sidebar.text_input("Enter Output Folder Path", "output")

# 获取文件列表
image_files = []
label_files = []
ends = ["tif", "jpg", "png"]

if images_folder:
    with st.spinner("Extracting images folder..."):
        with ZipFile(images_folder) as z:
            extract_path = Path("uploaded_images")
            z.extractall(extract_path)
            image_files = sorted(
                [
                    file
                    for file in extract_path.rglob("*")
                    if file.is_file() and file.suffix[1:] in ends
                ]
            )

if labels_folder:
    with st.spinner("Extracting labels folder..."):
        with ZipFile(labels_folder) as z:
            extract_path = Path("uploaded_labels")
            z.extractall(extract_path)
            label_files = sorted(
                [
                    file
                    for file in extract_path.rglob("*")
                    if file.is_file() and file.suffix[1:] in ends
                ]
            )

# Streamlit session_state
if "current_index" not in st.session_state:
    st.session_state.current_index = 0


# 修改复制函数
def copy_to_output(image_path, label_path):
    # if not output_folder or not os.path.exists(output_folder):
    #     st.warning("Please provide a valid output folder path.")
    #     return

    # 获取输出图像和标签的文件名
    image_filename = os.path.basename(image_path)
    label_filename = os.path.basename(label_path)

    # 构建输出文件夹路径
    output_image_folder = os.path.join(output_folder, "images")
    output_label_folder = os.path.join(output_folder, "labels")

    # 确保输出文件夹存在
    os.makedirs(output_image_folder, exist_ok=True)
    os.makedirs(output_label_folder, exist_ok=True)

    # 构建输出文件路径
    output_image_path = os.path.join(output_image_folder, image_filename)
    output_label_path = os.path.join(output_label_folder, label_filename)

    # 复制图像和标签到输出文件夹的相应子文件夹
    shutil.copy(image_path, output_image_path)
    shutil.copy(label_path, output_label_path)

    st.success("Image and label copied to the output folder.")


st.title("🤖 Image Label Viewer and Copy 🤖")

# 显示当前图像和标签
if image_files and label_files:
    current_image = str(image_files[st.session_state.current_index])
    current_label = str(label_files[st.session_state.current_index])

    st.write("Image Path:", current_image)
    st.write("Label Path:", current_label)
    st.write("Image exists:", os.path.exists(current_image))
    st.write("Label exists:", os.path.exists(current_label))
    tcol1, tcol2 = st.columns(2)
    # 显示当前文件名和排序位置
    st.write(f"🚀 Current File: {os.path.basename(current_image)}")
    st.write(
        f"🚨 Sort Position: {st.session_state.current_index + 1} / {len(image_files)}"
    )

    image = Image.open(current_image)
    tcol1.image(image, caption="Current Image", use_column_width="auto")
    # 使用PIL加载并显示标签图像
    label = Image.open(current_label)
    tcol2.image(label, caption="Current Label", use_column_width="auto")

    # 添加上一张和下一张按钮
    col1, col2, col3 = st.columns(3)

    def on_previous_click():
        st.session_state.current_index = max(0, st.session_state.current_index - 1)

    def on_next_click():
        st.session_state.current_index = min(
            len(image_files) - 1, st.session_state.current_index + 1
        )

    col1.button("< -  Previous", on_click=on_previous_click)
    col2.button("Next  - >", on_click=on_next_click)

    # 添加复制按钮
    if col3.button("Copy to Output Folder"):
        copy_to_output(current_image, current_label)
