# formulas
def jam_ke_detik(jam, menit, detik):
    jumlah_detik = (jam * 3600) + (menit * 60) + detik
    return jumlah_detik


# config
bot_version = "1.3 Release"
api_version = "1.2 Release"

initial_cogs = ['slash']

use_backup = True
full_backup = False
backup_time = jam_ke_detik(6, 0, 0) # format(jam, menit, detik)

update_embed = True
embed_reload_time = 600 # detik