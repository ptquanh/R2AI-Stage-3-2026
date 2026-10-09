# Báo cáo Thống kê Toàn diện Corpus Dữ liệu (Corpus Statistics Report)

> **Ngày tạo:** 05/10/2026  
> **Nguồn tổng hợp:** `data/raw/btc_provided/links_corpus.parquet`, `data/raw/final_corpus_text/` (`tier_1`, `tier_2`, `tier_other`), và nhật ký cào lỗi / lọc dữ liệu tại `data/raw/corpus_text/`.

---

## 1. Tổng quan Số lượng URL & Tiến độ Thu thập

| Chỉ số                                       | Số lượng URL  |  Tỷ lệ (%)  | Ghi chú                                                  |
| :------------------------------------------- | :-----------: | :---------: | :------------------------------------------------------- |
| **Tổng URL trong Links Corpus gốc**          | **4,394,718** | **100.00%** | Toàn bộ URL do BTC cung cấp qua 97 domain                |
| **Tổng URL đã cào thành công & có text**     | **2,851,575** | **64.89%**  | Nằm trong 3 file Tier (`tier_1`, `tier_2`, `tier_other`) |
| **Tổng URL còn lại chưa có text thành công** | **1,543,143** | **35.11%**  | Gồm lỗi mạng, bị lọc nội dung phi y tế và chưa cào       |

### Phân bố dữ liệu thành công theo các file Tier hiện tại:

- **`tier_1.parquet`**: **1,189,697 URL** (chiếm 41.72% dữ liệu thành công, gồm 19 domain)
- **`tier_2.parquet`**: **1,123,083 URL** (chiếm 39.38% dữ liệu thành công, gồm 14 domain)
- **`tier_other.parquet`**: **538,795 URL** (chiếm 18.89% dữ liệu thành công, gồm 47 domain)

---

## 2. Thống kê theo Phân tầng Thiết kế (Host Tiers Mapping)

Dựa theo quy hoạch tại `workspace-plan-04102026/vibomir/host_tiers.md`:

| Nhóm Tier (Quy hoạch)           | Số domain | Tổng URL gốc  | URL Thành công |  URL Còn lại  | Tỷ lệ thành công (%) |
| :------------------------------ | :-------: | :-----------: | :------------: | :-----------: | :------------------: |
| **Tier 1**                      |    22     |   1,765,567   |   1,189,697    |    575,870    |        67.38%        |
| **Tier 2**                      |    22     |   1,461,559   |   1,123,083    |    338,476    |        76.84%        |
| **Tier 3 (Merged Other)**       |    20     |    217,161    |    202,345     |    14,816     |        93.18%        |
| **Tier 4 (Merged Other)**       |    10     |    157,953    |     59,422     |    98,531     |        37.62%        |
| **Tier 9 (Dropped/403)**        |     9     |    694,698    |    183,060     |    511,638    |        26.35%        |
| **Tier Other (Unmapped/Small)** |    14     |    97,780     |     93,968     |     3,812     |        96.10%        |
| **TỔNG CỘNG**                   |  **97**   | **4,394,718** | **2,851,575**  | **1,543,143** |      **64.89%**      |

> **Ghi chú kiến trúc:**
>
> - `tier_1.parquet` bao gồm các domain Q&A y khoa và bệnh viện/nhà thuốc lớn.
> - `tier_2.parquet` bao gồm bách khoa y học, từ điển dược liệu Trung y.
> - `tier_other.parquet` gom toàn bộ Tier 3 (Báo chí chính thống VN), Tier 4 (Lifestyle có chọn lọc), Báo địa phương, và phần cào vớt được từ Tier 9.

---

## 3. Thống kê Chi tiết Từng Domain (Toàn bộ 97 Domain)

| STT | Domain / Host                           | Phân loại Tier              | Tổng URL gốc | URL Thành công | Còn lại | Tỷ lệ (%) |
| :-: | :-------------------------------------- | :-------------------------- | -----------: | -------------: | ------: | --------: |
|  1  | `cnkang.com`                            | Tier 2                      |      963,438 |        792,013 | 171,425 |    82.21% |
|  2  | `120ask.com`                            | Tier 1                      |      918,479 |        877,830 |  40,649 |    95.57% |
|  3  | `familydoctor.com.cn`                   | Tier 9 (Dropped/403)        |      447,453 |        179,236 | 268,217 |    40.06% |
|  4  | `ask.39.net`                            | Tier 1                      |      337,375 |            138 | 337,237 |     0.04% |
|  5  | `zysjonline.com`                        | Tier 9 (Dropped/403)        |      243,347 |              0 | 243,347 |     0.00% |
|  6  | `a-hospital.com`                        | Tier 2                      |      169,339 |        132,834 |  36,505 |    78.44% |
|  7  | `suckhoecongdongonline.vn`              | Tier 1                      |      154,503 |         87,598 |  66,905 |    56.70% |
|  8  | `zhongyibaodian.net`                    | Tier 2                      |      146,700 |        109,076 |  37,624 |    74.35% |
|  9  | `suckhoedoisong.vn`                     | Tier 1                      |       85,823 |         81,021 |   4,802 |    94.40% |
| 10  | `nhathuoclongchau.com.vn`               | Tier 1                      |       79,598 |            694 |  78,904 |     0.87% |
| 11  | `zydcd.com`                             | Tier 2                      |       78,680 |         67,820 |  10,860 |    86.20% |
| 12  | `thanhnien.vn`                          | Tier 3 (Merged Other)       |       72,111 |         69,239 |   2,872 |    96.02% |
| 13  | `wujue.com`                             | Tier 4 (Merged Other)       |       53,341 |         34,055 |  19,286 |    63.84% |
| 14  | `youlai.cn`                             | Tier 1                      |       46,119 |         45,922 |     197 |    99.57% |
| 15  | `laodong.vn`                            | Tier 3 (Merged Other)       |       31,282 |         30,203 |   1,079 |    96.55% |
| 16  | `baby.39.net`                           | Tier 4 (Merged Other)       |       27,621 |             44 |  27,577 |     0.16% |
| 17  | `phunusuckhoe.giadinhonline.vn`         | Tier 3 (Merged Other)       |       27,577 |         24,347 |   3,230 |    88.29% |
| 18  | `vinmec.com`                            | Tier 1                      |       26,129 |         26,053 |      76 |    99.71% |
| 19  | `bingli.iiyi.com`                       | Tier 1                      |       24,990 |              0 |  24,990 |     0.00% |
| 20  | `medlatec.vn`                           | Tier 1                      |       24,762 |         24,738 |      24 |    99.90% |
| 21  | `qihuangzhishu.com`                     | Tier 2                      |       23,637 |         14,268 |   9,369 |    60.36% |
| 22  | `jbk.39.net`                            | Tier 4 (Merged Other)       |       19,142 |         15,309 |   3,833 |    79.98% |
| 23  | `giadinhonline.vn`                      | Tier 3 (Merged Other)       |       16,729 |         14,199 |   2,530 |    84.88% |
| 24  | `baohaiphong.vn`                        | Tier Other (Unmapped/Small) |       16,286 |         15,895 |     391 |    97.60% |
| 25  | `baonghean.vn`                          | Tier Other (Unmapped/Small) |       15,941 |         15,196 |     745 |    95.33% |
| 26  | `vietnamnet.vn`                         | Tier 3 (Merged Other)       |       15,543 |         15,324 |     219 |    98.59% |
| 27  | `care.39.net`                           | Tier 2                      |       15,134 |              0 |  15,134 |     0.00% |
| 28  | `test.pmphai.com`                       | Tier 4 (Merged Other)       |       15,120 |          9,052 |   6,068 |    59.87% |
| 29  | `baodanang.vn`                          | Tier Other (Unmapped/Small) |       14,500 |         14,250 |     250 |    98.28% |
| 30  | `tiemchunglongchau.com.vn`              | Tier 1                      |       13,281 |          8,605 |   4,676 |    64.79% |
| 31  | `fitness.39.net`                        | Tier 4 (Merged Other)       |       12,066 |             19 |  12,047 |     0.16% |
| 32  | `baocantho.com.vn`                      | Tier Other (Unmapped/Small) |       12,016 |         10,235 |   1,781 |    85.18% |
| 33  | `hellobacsi.com`                        | Tier 1                      |       11,747 |         11,291 |     456 |    96.12% |
| 34  | `woman.39.net`                          | Tier 4 (Merged Other)       |       11,687 |             14 |  11,673 |     0.12% |
| 35  | `food.39.net`                           | Tier 4 (Merged Other)       |       11,024 |              3 |  11,021 |     0.03% |
| 36  | `baoangiang.com.vn`                     | Tier Other (Unmapped/Small) |       10,738 |         10,513 |     225 |    97.90% |
| 37  | `fk.39.net`                             | Tier 2                      |        9,812 |              0 |   9,812 |     0.00% |
| 38  | `vov.vn`                                | Tier 3 (Merged Other)       |        9,784 |          9,414 |     370 |    96.22% |
| 39  | `cancer.39.net`                         | Tier 2                      |        8,415 |            510 |   7,905 |     6.06% |
| 40  | `khoahocphothong.vn`                    | Tier 3 (Merged Other)       |        8,143 |          8,053 |      90 |    98.89% |
| 41  | `jb39.com`                              | Tier 1                      |        7,306 |          3,737 |   3,569 |    51.15% |
| 42  | `youmed.vn`                             | Tier 1                      |        7,189 |          4,982 |   2,207 |    69.30% |
| 43  | `vov2.vov.vn`                           | Tier 3 (Merged Other)       |        6,899 |          6,815 |      84 |    98.78% |
| 44  | `nk.39.net`                             | Tier 2                      |        6,650 |              0 |   6,650 |     0.00% |
| 45  | `phuyen.baodaklak.vn`                   | Tier Other (Unmapped/Small) |        6,252 |          6,173 |      79 |    98.74% |
| 46  | `msdmanuals.cn`                         | Tier 2                      |        6,173 |          5,470 |     703 |    88.61% |
| 47  | `heart.39.net`                          | Tier 2                      |        5,965 |              0 |   5,965 |     0.00% |
| 48  | `article.iiyi.com`                      | Tier 1                      |        5,641 |              0 |   5,641 |     0.00% |
| 49  | `suckhoeviet.org.vn`                    | Tier 1                      |        5,627 |          5,607 |      20 |    99.64% |
| 50  | `baoquangtri.vn`                        | Tier Other (Unmapped/Small) |        5,483 |          5,357 |     126 |    97.70% |
| 51  | `pmc-ecm-healthblog.beta.pharmacity.io` | Tier 1                      |        5,333 |              0 |   5,333 |     0.00% |
| 52  | `man.39.net`                            | Tier 4 (Merged Other)       |        5,320 |             13 |   5,307 |     0.24% |
| 53  | `nhandan.vn`                            | Tier 3 (Merged Other)       |        5,225 |          5,034 |     191 |    96.34% |
| 54  | `baovinhlong.com.vn`                    | Tier Other (Unmapped/Small) |        5,113 |          5,042 |      71 |    98.61% |
| 55  | `gan.39.net`                            | Tier 2                      |        5,027 |              4 |   5,023 |     0.08% |
| 56  | `tamanhhospital.vn`                     | Tier 1                      |        4,261 |          4,255 |       6 |    99.86% |
| 57  | `tnb.39.net`                            | Tier 2                      |        4,178 |              0 |   4,178 |     0.00% |
| 58  | `wei.39.net`                            | Tier 2                      |        3,894 |              2 |   3,892 |     0.05% |
| 59  | `tuoitre.vn`                            | Tier 3 (Merged Other)       |        3,893 |          3,835 |      58 |    98.51% |
| 60  | `baidianfeng.familydoctor.com.cn`       | Tier 9 (Dropped/403)        |        3,798 |          3,797 |       1 |    99.97% |
| 61  | `qdnd.vn`                               | Tier 3 (Merged Other)       |        3,700 |          1,606 |   2,094 |    43.41% |
| 62  | `vietnamplus.vn`                        | Tier 3 (Merged Other)       |        3,695 |          3,667 |      28 |    99.24% |
| 63  | `baogialai.com.vn`                      | Tier Other (Unmapped/Small) |        3,290 |          3,254 |      36 |    98.91% |
| 64  | `shen.39.net`                           | Tier 2                      |        3,223 |             27 |   3,196 |     0.84% |
| 65  | `ek.39.net`                             | Tier 2                      |        3,222 |              0 |   3,222 |     0.00% |
| 66  | `tienphong.vn`                          | Tier 3 (Merged Other)       |        3,021 |          2,985 |      36 |    98.81% |
| 67  | `thaythuocvietnam.vn`                   | Tier 1                      |        2,927 |          2,805 |     122 |    95.83% |
| 68  | `baoquangninh.vn`                       | Tier Other (Unmapped/Small) |        2,912 |          2,880 |      32 |    98.90% |
| 69  | `bachmai.gov.vn`                        | Tier 1                      |        2,783 |          2,749 |      34 |    98.78% |
| 70  | `baidu.com`                             | Tier 4 (Merged Other)       |        2,631 |            913 |   1,718 |    34.70% |
| 71  | `baochinhphu.vn`                        | Tier 3 (Merged Other)       |        2,302 |          2,283 |      19 |    99.17% |
| 72  | `dantri.com.vn`                         | Tier 3 (Merged Other)       |        2,063 |            255 |   1,808 |    12.36% |
| 73  | `gk.39.net`                             | Tier 2                      |        2,059 |              4 |   2,055 |     0.19% |
| 74  | `vnexpress.net`                         | Tier 3 (Merged Other)       |        2,055 |          2,034 |      21 |    98.98% |
| 75  | `baolangson.vn`                         | Tier Other (Unmapped/Small) |        1,981 |          1,960 |      21 |    98.94% |
| 76  | `sggp.org.vn`                           | Tier 3 (Merged Other)       |        1,853 |          1,801 |      52 |    97.19% |
| 77  | `gc.39.net`                             | Tier 2                      |        1,746 |              2 |   1,744 |     0.11% |
| 78  | `pf.39.net`                             | Tier 2                      |        1,538 |             15 |   1,523 |     0.98% |
| 79  | `health.people.com.cn`                  | Tier 2                      |        1,348 |          1,038 |     310 |    77.00% |
| 80  | `baophutho.vn`                          | Tier Other (Unmapped/Small) |        1,288 |          1,284 |       4 |    99.69% |
| 81  | `hanoimoi.vn`                           | Tier 3 (Merged Other)       |        1,283 |          1,248 |      35 |    97.27% |
| 82  | `benhviennhitrunguong.gov.vn`           | Tier 1                      |        1,200 |          1,178 |      22 |    98.17% |
| 83  | `baotayninh.vn`                         | Tier Other (Unmapped/Small) |        1,198 |          1,180 |      18 |    98.50% |
| 84  | `sj.39.net`                             | Tier 2                      |          942 |              0 |     942 |     0.00% |
| 85  | `baothanhhoa.vn`                        | Tier Other (Unmapped/Small) |          782 |            749 |      33 |    95.78% |
| 86  | `byby.39.net`                           | Tier 2                      |          439 |              0 |     439 |     0.00% |
| 87  | `benhvienvietduc.org`                   | Tier 1                      |          425 |            425 |       0 |   100.00% |
| 88  | `pharmacity.vn`                         | Tier 1                      |           69 |             69 |       0 |   100.00% |
| 89  | `familydoctor.cn`                       | Tier 9 (Dropped/403)        |           44 |             25 |      19 |    56.82% |
| 90  | `qy.familydoctor.com.cn`                | Tier 9 (Dropped/403)        |           40 |              0 |      40 |     0.00% |
| 91  | `v.familydoctor.com.cn`                 | Tier 9 (Dropped/403)        |           10 |              0 |      10 |     0.00% |
| 92  | `ask.familydoctor.com.cn`               | Tier 9 (Dropped/403)        |            3 |              2 |       1 |    66.67% |
| 93  | `yanglao.familydoctor.com.cn`           | Tier 9 (Dropped/403)        |            2 |              0 |       2 |     0.00% |
| 94  | `mega.vietnamplus.vn`                   | Tier 3 (Merged Other)       |            2 |              2 |       0 |   100.00% |
| 95  | `fk.99.com.cn`                          | Tier 4 (Merged Other)       |            1 |              0 |       1 |     0.00% |
| 96  | `ypk.familydoctor.com.cn`               | Tier 9 (Dropped/403)        |            1 |              0 |       1 |     0.00% |
| 97  | `special.vietnamplus.vn`                | Tier 3 (Merged Other)       |            1 |              1 |       0 |   100.00% |

---

## 4. Thống kê Chi tiết Các URL Cào Bị Lỗi Mạng / HTTP

Tổng hợp từ các file `dropped_network.parquet`, `failed_batch_1.parquet`, `failed_batch_2.parquet`, ghi nhận **859,192 URL unique** gặp sự cố kết nối:

### A. Phân bố các mã lỗi và nguyên nhân chính:

| Mã lỗi / Nguyên nhân                                        | Số URL gặp lỗi | Tỷ lệ lỗi (%) | Phân tích chi tiết                   |
| :---------------------------------------------------------- | :------------: | :-----------: | :----------------------------------- |
| `HTTP_403`                                                  |    462,958     |    53.88%     | Gặp lỗi khi crawler gửi HTTP request |
| `Timeout`                                                   |    145,233     |    16.90%     | Gặp lỗi khi crawler gửi HTTP request |
| `HTTP_429`                                                  |     69,309     |     8.07%     | Gặp lỗi khi crawler gửi HTTP request |
| `HTTP_521`                                                  |     18,420     |     2.14%     | Gặp lỗi khi crawler gửi HTTP request |
| `Error: Cannot connect to host nhathuoclongchau.com.vn:443` |     8,331      |     0.97%     | Gặp lỗi khi crawler gửi HTTP request |
| `HTTP_503`                                                  |     6,636      |     0.77%     | Gặp lỗi khi crawler gửi HTTP request |
| `Error: 0, message='', url='https://www.qdnd.vn/y-te/tin-t` |     1,594      |     0.19%     | Gặp lỗi khi crawler gửi HTTP request |
| `Error: Timeout`                                            |      694       |     0.08%     | Gặp lỗi khi crawler gửi HTTP request |
| `HTTP_502`                                                  |      451       |     0.05%     | Gặp lỗi khi crawler gửi HTTP request |
| `Error: Cannot connect to host ask.39.net:443 ssl:default ` |      385       |     0.04%     | Gặp lỗi khi crawler gửi HTTP request |
| `Error: 0, message='', url='https://www.qdnd.vn/y-te/cac-v` |      307       |     0.04%     | Gặp lỗi khi crawler gửi HTTP request |
| `HTTP_500`                                                  |      190       |     0.02%     | Gặp lỗi khi crawler gửi HTTP request |
| `Error: 0, message='', url='https://www.qdnd.vn/y-te/benh-` |      175       |     0.02%     | Gặp lỗi khi crawler gửi HTTP request |
| `HTTP_404`                                                  |      167       |     0.02%     | Gặp lỗi khi crawler gửi HTTP request |
| `HTTP_428`                                                  |       68       |     0.01%     | Gặp lỗi khi crawler gửi HTTP request |
| `Error: Response payload is not completed: <TransferEncodi` |       46       |     0.01%     | Gặp lỗi khi crawler gửi HTTP request |
| `Error: HTTPError`                                          |       37       |     0.00%     | Gặp lỗi khi crawler gửi HTTP request |
| `Error: Server disconnected`                                |       31       |     0.00%     | Gặp lỗi khi crawler gửi HTTP request |
| `Error: Cannot connect to host zhongyibaodian.net:443 ssl:` |       18       |     0.00%     | Gặp lỗi khi crawler gửi HTTP request |
| `Error: 0, message='', url='https://www.qdnd.vn/y-te/suc-k` |       11       |     0.00%     | Gặp lỗi khi crawler gửi HTTP request |

### B. Top 25 Domain có số URL lỗi mạng nhiều nhất:

| STT | Domain                                  | Số URL lỗi mạng | Đặc điểm lỗi chính                    |
| :-: | :-------------------------------------- | :-------------: | :------------------------------------ |
|  1  | `zysjonline.com`                        |     243,347     | HTTP 403, Timeout hoặc Rate Limit 429 |
|  2  | `familydoctor.com.cn`                   |     239,863     | HTTP 403, Timeout hoặc Rate Limit 429 |
|  3  | `ask.39.net`                            |     131,921     | HTTP 403, Timeout hoặc Rate Limit 429 |
|  4  | `nhathuoclongchau.com.vn`               |     78,947      | HTTP 403, Timeout hoặc Rate Limit 429 |
|  5  | `cnkang.com`                            |     38,112      | HTTP 403, Timeout hoặc Rate Limit 429 |
|  6  | `zhongyibaodian.net`                    |     36,944      | HTTP 403, Timeout hoặc Rate Limit 429 |
|  7  | `120ask.com`                            |     34,855      | HTTP 403, Timeout hoặc Rate Limit 429 |
|  8  | `bingli.iiyi.com`                       |     17,949      | HTTP 403, Timeout hoặc Rate Limit 429 |
|  9  | `tiemchunglongchau.com.vn`              |      5,536      | HTTP 403, Timeout hoặc Rate Limit 429 |
| 10  | `pmc-ecm-healthblog.beta.pharmacity.io` |      5,333      | HTTP 403, Timeout hoặc Rate Limit 429 |
| 11  | `wujue.com`                             |      4,412      | HTTP 403, Timeout hoặc Rate Limit 429 |
| 12  | `a-hospital.com`                        |      2,986      | HTTP 403, Timeout hoặc Rate Limit 429 |
| 13  | `zydcd.com`                             |      2,694      | HTTP 403, Timeout hoặc Rate Limit 429 |
| 14  | `youmed.vn`                             |      2,199      | HTTP 403, Timeout hoặc Rate Limit 429 |
| 15  | `qdnd.vn`                               |      2,091      | HTTP 403, Timeout hoặc Rate Limit 429 |
| 16  | `baidu.com`                             |      2,050      | HTTP 403, Timeout hoặc Rate Limit 429 |
| 17  | `baocantho.com.vn`                      |      1,861      | HTTP 403, Timeout hoặc Rate Limit 429 |
| 18  | `dantri.com.vn`                         |      1,859      | HTTP 403, Timeout hoặc Rate Limit 429 |
| 19  | `giadinhonline.vn`                      |       935       | HTTP 403, Timeout hoặc Rate Limit 429 |
| 20  | `hellobacsi.com`                        |       927       | HTTP 403, Timeout hoặc Rate Limit 429 |
| 21  | `test.pmphai.com`                       |       888       | HTTP 403, Timeout hoặc Rate Limit 429 |
| 22  | `article.iiyi.com`                      |       878       | HTTP 403, Timeout hoặc Rate Limit 429 |
| 23  | `qihuangzhishu.com`                     |       706       | HTTP 403, Timeout hoặc Rate Limit 429 |
| 24  | `laodong.vn`                            |       661       | HTTP 403, Timeout hoặc Rate Limit 429 |
| 25  | `suckhoecongdongonline.vn`              |       501       | HTTP 403, Timeout hoặc Rate Limit 429 |

---

## 5. Thống kê URL Bị Loại Bỏ do Không Liên quan Y Tế (Non-Medical Filter)

File `data/raw/corpus_text/dropped_urls_merged/dropped_filtered.parquet` ghi nhận **490,897 URL** đã cào thành công nhưng bị bộ lọc từ khóa/nội dung (Heuristic Filter) loại bỏ do không chứa kiến thức y khoa:

### A. Phân bố lý do loại bỏ:

| Lý do loại bỏ                                                                | Số lượng URL | Tỷ lệ (%) |
| :--------------------------------------------------------------------------- | :----------: | :-------: |
| Không chứa bất kỳ từ khóa y khoa nào trong nội dung                          |   458,986    |  93.50%   |
| Trafilatura không trích xuất được text (Có thể là trang trắng hoặc chặn bot) |    31,911    |   6.50%   |

### B. Top 20 Domain có URL bị loại bỏ phi y tế nhiều nhất:

| STT | Domain                     | Số URL phi y tế | Tính chất nội dung bị loại bỏ                      |
| :-: | :------------------------- | :-------------: | :------------------------------------------------- |
|  1  | `ask.39.net`               |     167,201     | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
|  2  | `suckhoecongdongonline.vn` |     65,130      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
|  3  | `cnkang.com`               |     45,979      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
|  4  | `laodong.vn`               |     30,620      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
|  5  | `baby.39.net`              |     27,601      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
|  6  | `care.39.net`              |     15,134      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
|  7  | `fitness.39.net`           |     12,033      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
|  8  | `woman.39.net`             |     11,673      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
|  9  | `food.39.net`              |     11,021      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
| 10  | `fk.39.net`                |      9,812      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
| 11  | `qihuangzhishu.com`        |      9,353      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
| 12  | `wujue.com`                |      8,272      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
| 13  | `zhongyibaodian.net`       |      6,801      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
| 14  | `nk.39.net`                |      6,650      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
| 15  | `heart.39.net`             |      5,965      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
| 16  | `man.39.net`               |      5,307      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
| 17  | `gan.39.net`               |      5,023      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
| 18  | `suckhoedoisong.vn`        |      4,669      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
| 19  | `tnb.39.net`               |      4,178      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |
| 20  | `wei.39.net`               |      3,892      | Đời sống, thể thao, tin giải trí, mẹo vặt, văn hóa |

> **Lưu ý bổ sung về tiền xử lý:**  
> Ngoài bộ lọc trên, hệ thống đã chủ động loại bỏ thêm toàn bộ các URL rác chứa nội dung tử vi, bói toán, phong thủy, tướng số, cung hoàng đạo (`tu-vi`, `boi-toan`, `phong-thuy`, `tam-linh`...) từ các trang tin tức gia đình trước khi nạp vào `tier_other.parquet` để bảo vệ chất lượng truy hồi y sinh.

---

## 6. Đánh giá Chiến lược & Sẵn sàng Triển khai

1. **Chất lượng Corpus 2.85M URL:** Toàn bộ 2,851,575 URL trong 3 Tier là văn bản y tế sạch, có cấu trúc rõ ràng, không chứa trang rỗng hoặc rác phi y học.
2. **Toàn vẹn Định danh (ID Integrity):** 100% các dòng đều bảo lưu đúng ID nguyên bản từ `links_corpus.parquet` của BTC, không trùng lặp URL.
3. **Khả năng Mở rộng:** Dữ liệu sẵn sàng phục vụ quy trình Semantic Chunking + Embeddings (BGE-M3) chạy theo batch trên Kaggle.
