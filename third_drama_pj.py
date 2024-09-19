import pymysql
db = pymysql.connect(host="192.168.1.80", port=3306,user="remo80", password="juzhun2023", database="zt")
cursor = db.cursor()

print('开始进行分类统计')
third_drama_sql = f"SELECT id FROM `zt_third_drama`"
cursor.execute(third_drama_sql)
third_dramas = cursor.fetchall()
for third in third_dramas:
    comment_num = 0
    digg_num = 0
    collect_num = 0
    t_num = third[0]
    print(t_num)
    total_count_sql = f"SELECT comment_count,digg_count,collect_count FROM `zt_author_data` WHERE drama_id={t_num}"
    cursor.execute(total_count_sql)
    total_counts = cursor.fetchall()
    if len(total_counts) != 0:
        for total in total_counts:
            comment_num += total[0]
            digg_num += total[1]
            collect_num += total[2]
        print(comment_num, digg_num, collect_num)
        update_drama_sql = f"UPDATE zt_third_drama SET comment_count = {comment_num}, digg_count = {digg_num},collect_count = {collect_num} WHERE id = {t_num}"
    else:
        update_drama_sql = f"UPDATE zt_third_drama SET comment_count = 0, digg_count = 0,collect_count = 0 WHERE id = {t_num}"
    cursor.execute(update_drama_sql)
    db.commit()
print('执行分类完毕')