path = "/home/luoxinyu/下载/1111.txt"
with open(path,"r",encoding="gbk") as f:
    flag = True
    txt = ""
    while flag:
        a = f.read(1)
        if a:
            if a in ["，","。","？","！"]:
                temp = "\n"
            else:
                temp = a
            txt+=temp
        else:
            flag = False
with open("/home/luoxinyu/下载/new_1111.txt","w",encoding = "gbk") as f:
    f.writelines(txt)
