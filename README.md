# Electrical Impedance Tomography
Electrical Impedance Tomography (EIT) adalah  suatu konsep pencitraan dari distribusi resistivitas  listrik  internal  suatu objek  dengan  pengukuran  beda potensial  listrik  antar  elektrode yang  terhubung  dengan objek.  Teknik  ini  bekerja  dengan  cara  menginjeksikan  arus listrik  pada  objek  melalui elektrode yang terpasang pada permukaan objek.

![EIT](https://github.com/agungdwiprasetyo/EIT/raw/master/pic/chickentiss.jpeg)

Repositori ini berisi program untuk merekonstruksi citra pada EIT berdasaran data tegangan yang diperoleh dari alat EIT yang telah dibuat. Program ditulis dalam bahasa pemrograman Python. Versi python yang digunakan yaitu versi 3 keatas.

Permasalahan  dalam  rekonstruksi citra  pada  EIT  dapat  dipecah menjadi  dua  yaitu Forward  Problem dan Inverse Problem. Penyelesaian Forward Problem dapat dilakukan dengan Finite Element Method (FEM). Kemudian teknik rekonstruksi untuk bagian inverse problem dalam program ini yaitu menggunakan algoritma BP (Back Projection), JAC (Gauss-Newton solver), dan Greit (menggunakan metode distribusi).

Ada tambahan satu algoritma rekonstruksi untuk Inverse Problem, yaitu Simultaneous Algebraic Reconstruction Technique (SART) yang terdapat dalam folder ``` /SART ```. Algoritma ini akan diselesaikan dengan teknik *paralell processing* menggunakan GPU (Graphic Processing Unit). Tujuannya yaitu untuk membandingkan kecepatan serta layak atau tidak digunakan dalam pencitraan EIT.

## Requirements

Versi python yang digunakan yaitu Python 3.5, dan menggunakan sistem operasi Linux 64-bit. Adapun beberapa library yang dibutuhkan supaya dapat menjalankan program dalam repositori ini adalah sebagai berikut:

| Library  | Shell script |
| ---- | ---- |
| **numpy** | ```$ sudo apt-get install python3-numpy``` |
| **scipy** | ```$ sudo apt-get install python3-scipy``` |
| **matplotlib** | ```$ sudo apt-get install python3-matplotlib``` |
| **vispy** | ```$ sudo apt-get install python3-vispy``` |
| **pandas** | ```$ sudo apt-get install python3-pandas``` |
| **xarray** | ```$ sudo apt-get install python3-xarray``` |
| **distmesh** | ```$ sudo apt-get install python3-distmesh``` |


## Rancangan Sistem

Dalam perancangan sistem ini dibagi menjadi 3 bagian utama yaitu penyelesaian Forward Problem, penyelesaian Inverse Problem, dan front-end untuk visualisasi citra. Secara garis besar, rancangan sistem dapat digambarkan sebagai berikut:

![sistem](https://github.com/agungdwiprasetyo/EIT/raw/master/pic/desainsistem.jpg)

1. **Penyelesaian Forward Problem:**
Pada bagian ini, data akuisisi dari perangkat EIT akan diolah oleh sebuah single board computer. Single board computer yang digunakan yaitu Raspberry Pi. Hasil luaran dari bagian ini adalah data hasil pengolahan dengan penyelesaian Forward Problem yang menggunakan7 Finite Element Method (FEM). Data ini selanjutnya akan dikirim ke server untuk diolah lebih lanjut melalui koneksi internet.
2. **Penyelesaian Inverse Problem:** 
Penyelesaian Inverse Problem ini terjadi pada server. Data dari langkah pada penyelesaian Forward Problem sebelumnya akan digunakan untuk penyelesaian Inverse Problem. Data yang diolah dalam proses Inverse Problem ini sangat besar, sehingga dimungkinkan akan dilakukan pemrosesan paralel menggunakan GPU (*Graphics Processing Unit*) pada server. Hasil luaran dari bagian ini yaitu citra yang sudah terbentuk untuk selanjutnya akan ditampilkan pada aplikasi web.
3. **Front-end untuk visualisasi citra:** 
Bagian ini menggunakan aplikasi web untuk memvisualisasikan citra hasil rekonstruksi yang diperoleh dari proses Inverse Problem pada server. Front-end untuk membangun aplikasi web ini menggunakan AngularJS.

## Tahapan

Apabila semua library yang dibutuhkan sudah terinstal, jalankan program **main.py** dengan mengetikkan perintah ```$ python3 main.py``` atau ```$ ./main.py```. Data yang digunakan masih *dummy* (data sembarang). Maka proses yang sedang berjalan yaitu dapat dilihat pada gambar dibawah ini:

![proses](https://github.com/agungdwiprasetyo/EIT/raw/master/pic/proses.png)

Pada proses diatas ditampilkan matriks yang telah diolah sedemikan rupa yang kemudian digunakan untuk rekonstruksi citra pada EIT.

Proses penyelesaian Forward Problem menghasilkan citra sebagai berikut:
![forward](https://github.com/agungdwiprasetyo/EIT/raw/master/pic/forwardproblem.png)

Sedangkan pada penyelesaian Inverse Problem (tahap akhir), dihasilkan citra sebagai berikut:
![inverse](https://github.com/agungdwiprasetyo/EIT/raw/master/pic/inverseproblem.png)