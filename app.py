from flask import Flask, render_template, request, flash
from MyQR import myqr
import time

app = Flask(__name__)

# 定义一个 secret_key，内容可随意指定，用于混入消息中进行加密
app.secret_key = "secret_key"


@app.route('/')
def index():
    # 展示渲染后的主页模板文件
    return render_template('index.html')


# -- 二维码导出功能 --
@app.route('/export', methods=["POST"])
def export():
    """上传文件函数，用于执行文件上传功能"""
    if request.method == "POST":
        url_str = request.form.get('url_str')
        if not url_str:
            url_str = "https://www.baidu.com/"

        upload_file = request.files.get('file')

        # 创建用于区分文件的13位时间戳
        time_str = str(int(round(time.time() * 1000)))

        # 如果没有上传图片
        if not upload_file:
            export_name = "qrcode_{}.png".format(time_str)
            export_path = "./static/export/{}".format(export_name)
            # 生成不含图片的普通二维码
            try:
                myqr.run(url_str, save_name=export_path)
            except Exception as e:
                flash("Error: {}".format(e))
                return index()
            # 定义展示图片的标识，show_photo 为 True，模板页面将会展示二维码
            show_photo = True

        # 如果上传了图片，保存图片并生成二维码
        else:
            file_name = upload_file.filename
            file_header = file_name.split(".")[0]
            file_type = file_name[-4:]
            print(file_type)
            # 如果后缀不符，展示提示信息，并跳转到主页
            if file_type not in ['.bmp', '.jpg', '.png', '.gif']:
                flash("文件格式错误，支持的文件格式为：bmp, jpg, png, gif")
                return index()

            # 定义上传图片的原始路径，用于存储图片
            save_path = "./static/origin/{}".format(upload_file.filename)
            upload_file.save(save_path)
            # 拼接导出文件的文件头部，后缀将在稍后判断
            export_header = "{}_{}".format(file_header, time_str)
            # 拼接导出路径
            if file_type in ['.bmp', '.jpg', '.png']:
                export_name = export_header + ".png"
                export_path = "./static/export/{}".format(export_name)
            elif file_type == ".gif":
                export_name = export_header + ".gif"
                export_path = "./static/export/{}".format(export_name)

            # 生成包含图片的二维码
            try:
                myqr.run(url_str, picture=save_path, colorized=True, save_name=export_path)
            except Exception as e:
                flash("Error: {}".format(e))
                return index()
            show_photo = True

        # 完成上传后，重新渲染模板页面
        return render_template('index.html', export_path=export_path,
                               show_photo=show_photo, export_name=export_name)


# -- 实现二维码图片下载功能 --
@app.route("/download/<file_name>")
def downoad(file_name):
    download_type = request.args.get("type")
    if download_type == "local":
        from flask import Response
        with open("./static/export/{}".format(file_name), "rb") as f:
            fp = f.read()
            response = Response(fp, content_type='application/octet-stream')
            # file_name需要进行编码转码，否则中文文件无法正常下载
            response.headers["Content-disposition"] = 'attachment; filename={}'.format(
                file_name.encode("utf-8").decode("latin-1"))
            return response


if __name__ == "__main__":
    # 定义监听host 为0.0.0.0，表示此服务器可以被外网访问
    # 默认端口为5000
    app.run(host="0.0.0.0")

