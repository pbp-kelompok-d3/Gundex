# 🏔️ Hello everyone, We are GunDex!

## 👥 Anggota Kelompok D03
- M. Adella Fathir Supriadi (2406495640)
- Rasyad Zulham Rabani (2406348540)
- Fairuz Akhtar Randrasyah (2406403955)
- Muhammad Alfa Mubarok (2406431391)
- Moch Raydzan (2406432482)

## 🌋 Apa itu GunDex? 
GunDex (singkatan dari Gunung Index) adalah platform web berbasis Django yang dirancang khusus untuk para pendaki gunung dan pencinta alam di Indonesia.
GunDex hadir sebagai solusi bagi para pendaki yang ingin menjelajahi informasi gunung-gunung di Indonesia, mencatat aktivitas pendakian mereka, dan berbagi pengalaman dengan komunitas lain.

Melalui GunDex, pengguna dapat dengan mudah:

🔎 Menjelajahi berbagai gunung di Indonesia lengkap dengan lokasi, ketinggian, dan jalur pendakiannya.

🎯 Menyimpan daftar impian pendakian lewat fitur Wishlist.

🥾 Mencatat riwayat pendakian pribadi melalui fitur Log Pendakian.

📰 Membaca dan menulis artikel pendakian untuk berbagi wawasan dan tips antar pengguna.

💬 Berinteraksi dengan komunitas pendaki lain melalui sistem akun pengguna yang aman dan personal.

GunDex dibangun dengan framework Django (MVT) serta memanfaatkan AJAX dan Tailwind CSS agar website terasa dinamis, modern, dan responsif di berbagai perangkat.


## 📕 Daftar Modul
👤 User (Akun & Profil)  
Dikerjakan oleh Fairuz Akhtar Randrasyah  
Fitur User menangani seluruh sistem akun di GunDex. Mulai dari registrasi, login, logout, hingga pengelolaan profil pengguna. Setiap pendaki yang membuat akun akan memiliki dashboard pribadi tempat mereka dapat melihat wishlist, log pendakian, dan mengubah data profil mereka seperti nama dan biodata singkat. Fitur ini juga memastikan keamanan data pengguna dengan sistem autentikasi bawaan Django. Melalui modul User, GunDex menghadirkan pengalaman yang lebih personal bagi setiap pendaki, menjadikan aplikasi ini bukan sekadar database gunung, tetapi juga ruang digital yang mencatat jejak perjalananmu sebagai seorang hiker sejati.

🏔️ Explore Gunung  
Dikerjakan oleh Rasyad Zulham Rabani  
Fitur Explore Gunung menjadi halaman utama dari GunDex, tempat para pengguna bisa menjelajahi berbagai gunung di Indonesia. Di sini, pendaki bisa mencari gunung berdasarkan nama dan provinsi dengan tampilan yang interaktif dan responsif. Setiap gunung memiliki halaman detail berisi informasi deskripsi, lokasi, dan ketinggian. Dengan fitur ini, para hiker tidak perlu bingung lagi ingin mendaki ke mana. Cukup buka GunDex, dan temukan gunung impianmu dengan mudah!

💡 Artikel  
Dikerjakan oleh M. Adella Fathir Supriadi   
Fitur Artikel berisi kumpulan tulisan dan tips yang informatif seputar dunia pendakian. Pengguna bisa membaca panduan keselamatan, rekomendasi gunung untuk pemula, serta tips menjaga stamina di medan terjal. Artikel juga dapat mencakup berita terbaru tentang kondisi gunung di Indonesia. Dengan fitur ini, GunDex menjadi tempat belajar dan berbagi ilmu, bukan hanya sekadar mencari data gunung. Setiap artikel ditulis untuk membantu pendaki mempersiapkan diri lebih matang sebelum memulai petualangan berikutnya. 

🎯 Wishlist  
Dikerjakan oleh Muhammad Alfa Mubarok  
Fitur Wishlist membantu pengguna menyimpan daftar gunung yang ingin mereka daki di masa mendatang. Setiap kali pengguna menemukan gunung menarik di halaman Explore, mereka dapat langsung menambahkannya ke daftar Wishlist. Fitur ini juga memungkinkan pengguna untuk menghapus atau menandai gunung yang ingin mereka daki, menjaga daftar impian tetap rapi dan ter-update. Dengan Wishlist, pengguna dapat merencanakan perjalanan pendakian mereka secara lebih personal dan terorganisir. Layaknya daftar target petualangan yang siap ditaklukkan satu per satu!

🥾 Log Pendakian  
Dikerjakan oleh Moch Raydzan  
Fitur Log Pendakian berfungsi sebagai jurnal pribadi pendaki untuk mencatat setiap pengalaman mendakinya. Pengguna dapat menulis tanggal mulai dan selesai pendakian, rating pendakian, jumlah orang dalam tim, serta kesan pribadi selama perjalanan. Semua log ini tersimpan dalam akun pengguna dan bersifat privat, sehingga hanya pemilik akun yang bisa melihat riwayat pendakiannya sendiri. Melalui fitur ini, setiap pendaki dapat melacak progres pendakiannya dari waktu ke waktu dan mengenang momen-momen berharga di puncak gunung favorit mereka. GunDex membuat setiap langkah pendakian tidak hanya berakhir di puncak, tetapi juga terekam selamanya di jurnal digitalmu!

## 📊 Initial Dataset
GunDex menggunakan dataset buatan sendiri yang berisi daftar gunung di Indonesia, mencakup nama gunung, lokasi, dan ketinggian.
Dataset dapat diakses melalui tautan berikut:
🔗 [Gunung Dataset – Google Sheets](https://docs.google.com/spreadsheets/d/10qIMDxK_dvc9FtDuoi80lleCl2Q33aeeAP5z4ca3opY/edit?gid=0#gid=0)
🔗 [Artikel Dataset – Google Sheets](https://docs.google.com/spreadsheets/d/1QE-WZKEFf2J9_1E28BfvxeYb3UW3XyNNvu1t9bg1E0k/edit?usp=sharing)


Beberapa data dikumpulkan dan disusun ulang dengan mengutip sumber terpercaya seperti

https://astacala.org/jalur-pendakian-gunung/

https://datagunung.com

## 🧍‍♂️🧗‍♀️ Jenis Pengguna
🛠️ Admin  
Admin memiliki peran sebagai pengelola utama sistem. Mereka bertanggung jawab untuk memperbarui dan menghapus data gunung, mengelola artikel pendakian, serta memantau aktivitas pengguna. Selain itu, admin juga memastikan bahwa setiap konten yang tampil di GunDex akurat dan sesuai dengan tujuan platform, yaitu menjadi sumber informasi terpercaya bagi pendaki di seluruh Indonesia.  

🥾 Hiker  
Hiker adalah pengguna umum yang memanfaatkan seluruh fitur GunDex. Mereka dapat melihat daftar gunung, menambah gunung ke wishlist, mencatat log pendakian pribadi, membaca artikel, dan mengelola akun mereka sendiri. Dengan akun pribadi, setiap hiker bisa menyimpan jejak pendakiannya dan membangun arsip perjalanan mereka dari waktu ke waktu. GunDex membantu para pendaki untuk tetap terhubung dengan alam, komunitas, dan diri mereka sendiri. Karena setiap pendakian punya cerita yang layak untuk diingat.


## Link PWS dan design
[https://rasyad.zulham-gundex.pbp.cs.ui.ac.id](https://rasyad-zulham-gundex.pbp.cs.ui.ac.id/)

https://www.figma.com/design/pBlQu8uLwuBH9aJQWKuQR0/Grand-Design?m=auto&t=gsURRZSHrJvA3pdE-1
