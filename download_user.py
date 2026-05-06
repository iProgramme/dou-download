import os
import sys
import subprocess
import shutil

# ==========================================
# 📋 请在这里粘贴你的抖音 Cookie
# ==========================================
# 获取方法：浏览器打开抖音 -> F12 -> 网络(Network) -> 刷新 
# -> 找一个请求 -> 请求头(Request Headers) -> 复制 cookie 的内容
USER_COOKIE = "bd_ticket_guard_client_web_domain=2; UIFID_TEMP=1092a36a2acc3ae8398deab3fd09104051338a3ad6cb249c7479b2d1664bb2d46a86615112bc420ba9616f72f358f7e7c9d166e5926ebe5ed2671bf4c46b98b064e8df17572874d73af65ff6122a2ced; hevc_supported=true; fpk1=U2FsdGVkX19YGnMHvA6G+l4l9jVZLpFX5BshA+5xQQ5rzMamzX4UBny9kYFNS3UVFYAzVUBHVvK1Ms146vq4tA==; fpk2=4ad072dfe5c14cff71c013c0dea8a6a3; UIFID=1092a36a2acc3ae8398deab3fd09104051338a3ad6cb249c7479b2d1664bb2d4d4914105c6f15e49eb8ad429b0a06ddf7fb10a4da432c718b0469f71499593e6abda802fb992f128058243c97d361c7f8644d460538416fc11b0dfc1f464cdfbe28865938c4a99de3d66f17861c8884c8c639cdd73c4d90432082a987cef2992681a33e97c0c4b553156256e1c2c458a49b3ab93e65ab1bfb0be38c14b3653ae; SearchMultiColumnLandingAbVer=2; SEARCH_RESULT_LIST_TYPE=%22multi%22; my_rd=2; enter_pc_once=1; xgplayer_device_id=93265631417; d_ticket=a1e31393fe35f6c9a954eada90feb1a1aaa7d; live_use_vvc=%22false%22; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; SelfTabRedDotControl=%5B%5D; tt_webid=7592052451793749555; __druidClientInfo=JTdCJTIyY2xpZW50V2lkdGglMjIlM0ExMDM4JTJDJTIyY2xpZW50SGVpZ2h0JTIyJTNBNzM0JTJDJTIyd2lkdGglMjIlM0ExMDM4JTJDJTIyaGVpZ2h0JTIyJTNBNzM0JTJDJTIyZGV2aWNlUGl4ZWxSYXRpbyUyMiUzQTIlMkMlMjJ1c2VyQWdlbnQlMjIlM0ElMjJNb3ppbGxhJTJGNS4wJTIwKE1hY2ludG9zaCUzQiUyMEludGVsJTIwTWFjJTIwT1MlMjBYJTIwMTBfMTVfNyklMjBBcHBsZVdlYktpdCUyRjUzNy4zNiUyMChLSFRNTCUyQyUyMGxpa2UlMjBHZWNrbyklMjBDaHJvbWUlMkYxNDQuMC4wLjAlMjBTYWZhcmklMkY1MzcuMzYlMjBFZGclMkYxNDQuMC4wLjAlMjIlN0Q=; __live_version__=%221.1.4.7838%22; PhoneResumeUidCacheV1=%7B%223987243889068467%22%3A%7B%22time%22%3A1769667003182%2C%22noClick%22%3A1%7D%7D; __security_mc_1_s_sdk_crypt_sdk=3d891d05-418e-9db1; __security_mc_1_s_sdk_cert_key=0c80358f-47ca-b7d7; passport_csrf_token=383701a6ff9fad9a1ebfcabb15e7ddd1; passport_csrf_token_default=383701a6ff9fad9a1ebfcabb15e7ddd1; use_biz_token=true; douyin.com; xg_device_score=7.495228914558955; device_web_cpu_core=8; s_v_web_id=verify_mnq32ujs_jS8zWyfT_GUvi_4ef0_BaSZ_TkO6gycUAlmU; is_dash_user=1; device_web_memory_size=16; SEARCH_UN_LOGIN_PV_CURR_DAY=%7B%22date%22%3A1776236092398%2C%22count%22%3A1%7D; passport_assist_user=CktXUhYThldpMPrawXu1ifbosoWvDZlCA1tBaEFVloL_8ynTmXepfYJeDTa9SdmIBiJbX-R1ygxdCKPbT00zoJD01dposTxPc-P6nm0aSgo8AAAAAAAAAAAAAFBORAVob6PPjCkGjiEkuIgaE3U2V1ReDg8BBtK6tr-ldb3xOYpI94dJlrq1p4pwzJasENfujg4Yia_WVCABIgEDBtA8GQ%3D%3D; sid_guard=9bee670ef4a119c6a57a2c7f0d0a40d0%7C1776236095%7C5184000%7CSun%2C+14-Jun-2026+06%3A54%3A55+GMT; uid_tt=21d38dbd752dd7cc01a9225b1001b679; uid_tt_ss=21d38dbd752dd7cc01a9225b1001b679; sid_tt=9bee670ef4a119c6a57a2c7f0d0a40d0; sessionid=9bee670ef4a119c6a57a2c7f0d0a40d0; sessionid_ss=9bee670ef4a119c6a57a2c7f0d0a40d0; session_tlb_tag=sttt%7C13%7Cm-5nDvShGcaleix_DQpA0P________-6wd3Px0XITua24nnzl3xR_2NgGIHaTzOYaOHe6HgcMb8%3D; is_staff_user=false; has_biz_token=false; sid_ucp_v1=1.0.0-KDE1YjI3MTdhN2ExMWFkODE3M2M1OTUwNzY0OGQ5NmZkNDIyM2VmMzIKIQizk5D9iMyKBxC_7PzOBhjvMSAMMIf1o6gGOAVA-wdIBBoCbHEiIDliZWU2NzBlZjRhMTE5YzZhNTdhMmM3ZjBkMGE0MGQw; ssid_ucp_v1=1.0.0-KDE1YjI3MTdhN2ExMWFkODE3M2M1OTUwNzY0OGQ5NmZkNDIyM2VmMzIKIQizk5D9iMyKBxC_7PzOBhjvMSAMMIf1o6gGOAVA-wdIBBoCbHEiIDliZWU2NzBlZjRhMTE5YzZhNTdhMmM3ZjBkMGE0MGQw; __security_mc_1_s_sdk_sign_data_key_web_protect=9e134835-4b27-8a22; login_time=1776236095441; _bd_ticket_crypt_cookie=b62fbf8785f6d16c521f576dff394cd8; csrf_session_id=c9759a587b7259b75ee83bdaedd07621; dy_swidth=1470; dy_sheight=956; strategyABtestKey=%221776655526.195%22; ttwid=1%7CmXqg3L40oX9-iwCiA-yYh2QaERk7ZUVI1ILY5iEeqwk%7C1776655526%7C473b202978673d3b7c1c02afc8944cf4e9bce6c562456f113fc3b35c0c4e0cae; publish_badge_show_info=%220%2C0%2C0%2C1776655531369%22; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1470%2C%5C%22screen_height%5C%22%3A956%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A16%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A0%7D%22; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAvI0x8J6GqhMLaXliSh8DqIasmiMh2xweDvahAUqDMj8y1lBWDbQMY1PIvy9YUt9P%2F1776700800000%2F0%2F0%2F1776657734659%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSHZNeVJwQmdXTVZMak9USDlRSENIMlVRVVE1NGhmVzNQWjFXbS9FTUtXL0VpbUZocE9NT0prM2Y4aUl6UHR5WDdQQTlSWjl1aWtPZFQ3eGxmbVpxWEk9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; home_can_add_dy_2_desktop=%221%22; odin_tt=08c182148a3657a14a6aec21886cf722de4f8a696e81234014999161776033a6ee37bd2f827e4939a21b35b450789006eda916f49f1ac84b527ff35bf930823df579945e6c247a892ab97c6320dedb7f; biz_trace_id=e15293f1; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAvI0x8J6GqhMLaXliSh8DqIasmiMh2xweDvahAUqDMj8y1lBWDbQMY1PIvy9YUt9P%2F1776700800000%2F0%2F1776657152417%2F0%22; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e582729277672715a646971273f2763646976602729277f6b5a666475273f2763646976602729276d6a6e5a6b6a716c273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f2730373734303c37333333323234272927676c715a75776a716a666a69273f2763646976602778; bit_env=K3_rMqNRHIjmTeMSTkE_14bCUBzcDV8Cepiwiw2YtDceQxFWJdNDUKFf0_UJ3DjqH0wZe4jYKoLeHRoXvGsPsWo5-1F7pCgxHMZ_pQoXh3_A02QneLNpAnK9bKIMAYu_SsIQd9Hj7r38EOBEQRwIsbzCTAyi6KbONtgTeLSySz8z-nfjPnS7ZjdSgc5-a_5EQTL1S-FvMvmDA74b64hd2Y57VdWlWI19AUEMdmRjltxvVve5b3SF6w0WD_bsKJerFOBcTJkK96pjl_IFbblHcMDj9sqpJ1OQ6Fv6x-VSGyLLYNDheH6pJdLE3NFYF_7VFQBiFPCNihH4YD8Wfvo4U6LzHx-IJtM194oyo46-kmWak4o6PnryPOOSUbTyXf3Mm3c5RHyBkkmDJ3XCmUr2bDP3gV9-TDL57UFPWSps1I0u2_nVgh8oas2vV1fiMOK5VXsynnGkPcqIa7FYWIXIftPddpJdDdezK6_e_OVU-Yk5kgPK_QfMjYFV4FmYEJe-LGBWBpRj5-C1-HZaiFGc5QyeZHcfdqcg5KGC869EoYWVufdUsQT7fN0CeRe6xeJi; gulu_source_res=eyJwX2luIjoiYjExMzYxNDM1NWVjYTlkNmE3MGE3MTk2Y2QzY2U1NTViZGJhNzRlNjQwM2IyYTI3OTM3NWE2YTRiYjVkMThhNyJ9; passport_auth_mix_state=7pfq1qynpvflo9saa86iz0x03788mfo7ayr1vmczs7a5p9pw; bd_ticket_guard_client_data_v2=eyJyZWVfcHVibGljX2tleSI6IkJIdk15UnBCZ1dNVkxqT1RIOVFIQ0gyVVFVUTU0aGZXM1BaMVdtL0VNS1cvRWltRmhwT01PSmszZjhpSXpQdHlYN1BBOVJaOXVpa09kVDd4bGZtWnFYST0iLCJ0c19zaWduIjoidHMuMi5kMzYzNTJlM2NjYzFhOWIxNjQ5MzY3YTYyOWRhMWIwY2VjNzZlNDkxYzY3OTllY2M2OWMzNWNkZmVkNjM4ZjkzYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiJ6S2pZYWJ3VW1ueWJpSE1MMmZIK3ZLZG9PZ2I5NUd3WDQ2cGZ2dG4vTi9FPSIsInNlY190cyI6IiNaQ3NvaGx0WXNkejh5OFVxZWozVmEwbk5vZnFmT1FObG9uTlBSYUZPbmtoYVVBUW9FZU50VWlvd25ZT3kifQ%3D%3D; IsDouyinActive=false; __ac_nonce=069e5ba290004f0123f4e; __ac_signature=_02B4Z6wo00f01ITcBTQAAIDCt0nzdJrioGCE.AGAAEjX1f" 
# ==========================================

def get_f2_path():
    f2_bin = shutil.which("f2")
    if f2_bin:
        return f2_bin
    
    possible_paths = [
        os.path.expanduser("~/.local/bin/f2"),
        "/usr/local/bin/f2",
        os.path.join(sys.prefix, "bin", "f2"),
        "/Library/Frameworks/Python.framework/Versions/3.13/bin/f2"
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return "f2"

def download_with_f2(user_url):
    if not USER_COOKIE:
        print("❌ 错误: 请先在 download_user.py 文件中填入你的 USER_COOKIE！")
        print("你可以用文本编辑器打开此文件，并在第 11 行粘贴你的 Cookie 字符串。")
        return

    print(f"🚀 Launching advanced downloader for: {user_url}")
    
    download_path = os.path.expanduser("~/Desktop/DouyinDownloader/downloads")
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    
    f2_path = get_f2_path()
    
    # ⚠️ 修正: f2 0.0.1.7 要求显式指定模式 (-M)
    # 对于博主主页视频，模式是 'post'
    cmd = [
        f2_path, "dy",
        "-u", user_url,
        "-p", download_path,
        "-k", USER_COOKIE,
        "-M", "post"  # 显式指定下载模式为博主发布的作品
    ]
    
    try:
        print(f"Starting f2 engine (mode: post, using manual cookie)...")
        # Run the command and stream output
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in process.stdout:
            print(line, end="")
            
        process.wait()
        
        if process.returncode == 0:
            print(f"\n✨ Process finished successfully!")
            print(f"Videos are saved in: {download_path}")
        else:
            print(f"\n❌ f2 exited with code {process.returncode}.")
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 download_user.py <douyin_user_url>")
    else:
        download_with_f2(sys.argv[1])
