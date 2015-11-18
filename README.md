1,这是我的第一个自学开发的爬虫后台工具，主要是模仿了其他的工具的实现，期望实现的功能是，能够更加方便快速的配置解析规则，并具备稳定，多线程爬取数据的能力，且灵活，功能强大，希望能在2016年３月１号完成并上线。——————2015．11.17
2,mysql数据库的创建:
        创建数据库（utf-8）：
        CREATE DATABASE `flaskTest`
        CHARACTER SET 'utf8'
        COLLATE 'utf8_general_ci';
        创建表：
        python manage.py shell
        from manage import db
        db.create_all()
3,git用的最多的命令：１，git status　２，git add -A　3，git commit -m "支持删除功能" 　4，git remote add origin03 git@github.com:guoronghua/CommonCrawler.git　５，git push -u origin03 thefirst01