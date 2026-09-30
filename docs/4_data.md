# 4. Data

## Dữ liệu cuộc thi

Ban Tổ chức cung cấp:

- **Danh sách nguồn dữ liệu:** các liên kết tới nguồn bài viết y khoa tiếng Việt và tiếng Trung để các đội chủ động thu thập, xử lý và xây dựng cơ sở tri thức phục vụ truy hồi. Đối với tiếng Anh, các đội có thể chủ động tìm kiếm tài liệu từ PubMed thông qua các API như NCBI Entrez E-utilities hoặc Europe PMC.
- **Bộ dữ liệu kiểm thử (test set):** tập câu hỏi bằng tiếng Việt, được sử dụng làm căn cứ chấm điểm và đánh giá hệ thống của các đội thi.

Ban Tổ chức không cung cấp quy trình embedding/indexing sẵn có. Các đội thi được toàn quyền chủ động trong việc:

- Xây dựng hoặc lựa chọn mô hình embedding đa ngôn ngữ phù hợp với dữ liệu y học.
- Thiết kế chiến lược lập chỉ mục và tìm kiếm.
- Xây dựng cơ chế reranking, hậu xử lý.
- Các tập dữ liệu mở khác về y học mà đội thi có thể hợp pháp sử dụng để huấn luyện/đánh giá bổ trợ.

## Tập câu hỏi truy vấn

Tập câu hỏi truy vấn được cung cấp dưới dạng tệp JSONL. Mỗi dòng là một đối tượng JSON hợp lệ, gồm:

- `id`: Mã định danh của truy vấn, kiểu số nguyên (integer).
- `query`: Nội dung truy vấn y khoa bằng tiếng Việt, kiểu chuỗi (string).

```json
{
  "id": <integer>,
  "query": "<string>"
}
```

**Ví dụ:**

```json
{
  "id": 1,
  "query": "Cần làm gì đối với tình trạng tắc nghẽn đường tiết niệu do sỏi thận?"
}
```

## Nguồn dữ liệu được cung cấp

Đối với dữ liệu tiếng Việt và tiếng Trung, Ban Tổ chức cung cấp danh sách URL của các bài viết y khoa dưới dạng tệp JSONL. Mỗi dòng là một đối tượng JSON hợp lệ, gồm:

- `id`: Mã định danh của nguồn, kiểu số nguyên (integer).
- `url`: URL dẫn tới bài viết gốc, kiểu chuỗi (string).

```json
{
  "id": <integer>,
  "url": "<string>"
}
```

**Ví dụ:**

```json
{
  "id": 1,
  "url": "https://example.com/article"
}
```

Các đội tự thực hiện việc thu thập nội dung từ các URL được cung cấp, tiền xử lý, phân đoạn và xây dựng cơ sở tri thức phục vụ truy hồi.

Đối với dữ liệu tiếng Anh, Ban Tổ chức không cung cấp sẵn danh sách tài liệu. Phạm vi dữ liệu tiếng Anh được giới hạn ở các bài thuộc PubMed (cơ sở dữ liệu lớn về các công bố trong lĩnh vực y sinh và khoa học sức khỏe).

Các đội cần chủ động tìm kiếm các bài PubMed phù hợp với từng câu hỏi và thu thập nội dung để xây dựng cơ sở tri thức. Có thể sử dụng một số API như:

- **NCBI Entrez E-utilities:** dùng để tìm kiếm trực tiếp trên PubMed và lấy danh sách PMID - mã định danh của mỗi bản ghi PubMed.
- **Europe PMC API:** cũng có thể dùng để tìm kiếm các bản ghi PubMed, khi sử dụng cần giới hạn kết quả ở nguồn PubMed.
- **PubTator API:** có thể dùng để lấy nội dung của các bài PubMed theo PMID, bao gồm tiêu đề, abstract và các thông tin y sinh được trích xuất từ bài.

**Ví dụ:** với truy vấn `kidney stone urinary obstruction`, có thể sử dụng NCBI ESearch để lấy danh sách PMID của các bài PubMed phù hợp:

```bash
curl --get "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi" \
  --data-urlencode "db=pubmed" \
  --data-urlencode "term=kidney stone urinary obstruction" \
  --data-urlencode "retmax=100" \
  --data-urlencode "retmode=json"
```

Hoặc sử dụng Europe PMC API và giới hạn kết quả ở các bản ghi thuộc PubMed:

```bash
curl --get "https://www.ebi.ac.uk/europepmc/webservices/rest/search" \
  --data-urlencode "query=SRC:MED AND (kidney stone urinary obstruction)" \
  --data-urlencode "format=json" \
  --data-urlencode "pageSize=100"
```

Sau khi có PMID, có thể sử dụng PubTator API để lấy nội dung của bài. Ví dụ với PMID 26739349:

```bash
curl --get \
  "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocjson" \
  --data-urlencode "pmids=26739349"
```
