1,insatll mysql:  
       sudo apt-get install mysql
       sudo apt-get install libmysqlclient-dev
       sudo apt-get install python-pip
       sudo pip install -U pip
       sudo apt-get install python-dev libmysqlclient-dev
       sudo pip install MySQL-python
       sudo apt-get install mysql-workbench

2,mysql数据库的创建:
        创建数据库（utf-8）：
        CREATE DATABASE `c`
        CHARACTER SET 'utf8'
        COLLATE 'utf8_general_ci';
        创建表：
        python manage.py shell
        from manage import db
        db.create_all()

3,git用的最多的命令：１，git status　２，git add -A　3，git commit -m "支持删除功能" 　4，git remote add origin03 git@github.com:guoronghua/CommonCrawler.git　５，git push -u origin03 thefirst01

