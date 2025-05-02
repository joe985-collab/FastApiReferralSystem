import random, string

my_referral_code_list = {''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))+"\n" for x in range(50)}

with open("store_code.txt","w",encoding="utf-8") as f:
    f.writelines(my_referral_code_list)


