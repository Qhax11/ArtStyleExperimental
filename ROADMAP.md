# Giydirme Oyunu Yol Haritası

Son güncelleme: 2026-11-04

## Projenin amacı

Proje en temelinde bir **giysi giydirme oyunu**. Oyuncu, sabit kamerada duran anime tarzı karakteri arayüzden seçtiği kıyafet, saç ve aksesuarlarla giydirir, kombinini tamamlayıp finalize eder.

Oyun cozy bir hava taşır ve hediye olarak yapılıyor, satılmayacak. Karakter hediye edilen kişinin anime hali olduğu için benzerlik ve kişisel dokunuşlar, içerik sayısından daha önemli.

**Oyuncunun değiştirebilecekleri:**

- **Giysiler:** Üst, alt, elbise, dış giyim, çorap, ayakkabı
- **Saç:** Farklı saç modelleri ve renkleri
- **Aksesuarlar:** Gözlük, küpe, kolye, şapka
- **Çantalar:** Tipine göre omuzda, elde, çapraz veya sırtta

## Mevcut durum

- UE 5.8, `ArtStyleExperimental` projesi, içerik `/Game/DressUp/` altında
- Model VRoid Studio ile hazırlandı (`evrar.vroid`), benzerlik ayarları henüz bitmedi
- VRM4U plugin'i `Plugins/VRM4U` içinde kurulu
- Model `/Game/DressUp/Character` altına MToon materyalleriyle aktarıldı (ana mesh: `SK_evrar`)
- Tişört, şort ve ayakkabı şimdilik modelle birlikte geliyor, ayrı parça değil

## Kararlar

| Konu | Karar | Neden |
|---|---|---|
| Karakter | VRoid, anime tarzı | Benzerlik ve kıyafet uydurma daha kolay, cozy hava kendiliğinden geliyor |
| Aktarım | VRM → VRM4U, MToon | Toon görünümü ve yüz ifadeleri hazır geliyor |
| Giysiler | Child Skeletal Mesh + Leader Pose | Hafif ve kurması basit, vücut animasyonunu aynen takip eder |
| Aksesuarlar | Socket'e bağlı Static Mesh | Bükülmeleri gerekmiyor |
| Saç | Ayrı, değiştirilebilir bir bölge | Saç modeli oyuncunun seçimlerinden biri |
| Çantalar | Tipine göre bağlantı noktası | Her çanta tipi vücutta farklı yerde durur |
| Vücut gizleme | Bölge maskesi dokusu | Mesh'i parçalamak gerekmiyor |
| Temel katman | Vücut dokusundaki siyah üst ve şort | Çıplak başlangıcın teknik faydası yok, karakter de gerçek birine dayanıyor |
| Mantık | Blueprint | MCP ile hızlı ilerliyor, C++ gerektiren bir ihtiyaç yok |

## Mimari

```text
BP_DressUpCharacter
└─ BodyMesh (ana iskelet ve animasyon)
   ├─ Hair                                    → Skeletal Mesh
   ├─ Top, Bottom, Dress, Outer, Socks, Shoes → Skeletal Mesh (Leader Pose)
   ├─ Glasses, Earrings, Necklace, Hat        → Static Mesh (socket)
   └─ Bag                                     → Çanta tipine göre socket veya Skeletal Mesh
```

Her bölge için baştan boş bir component bulunur. Takmak mesh atamak, çıkarmak mesh'i boşaltmak demektir.

- **`DA_Item`:** Ad, ikon, bölge, mesh, socket ve konum ayarı, renk seçenekleri, gizlediği vücut bölgeleri, engellediği bölgeler (elbise üst ve altı engeller).
- **`DA_CharacterBody`:** Vücut mesh'i, animasyon ve maske. Model değişince burası değişir.
- **`OutfitComponent`:** `Equip`, `Unequip`, `GetEquipped`, kombin kaydetme. Arayüz yalnızca bununla konuşur.

Yeni kıyafet eklemek kod gerektirmez, sadece yeni bir `DA_Item` oluşturulur.

### Saç

- Saç, vücuttan ayrı bir mesh olarak kendi bölgesinde durur. Modelde saç zaten ayrı materyallerle geliyor (`Hair`, `HairBack`).
- Saç vücut bölgesi gizlemez, ama şapka gibi parçalarla çakışabilir. Çakışan şapka ve saç çiftleri `DA_Item` kurallarıyla yönetilir.
- Renk değişimi materyal parametresiyle yapılır.
- **Açık konu:** Leader Pose, vücut iskeletinde olmayan saç kemiklerini oynatmaz. Farklı saç modellerinin kemikleri farklıysa saç fiziği için ayrı bir çözüm gerekir (Copy Pose veya kendi Anim Blueprint'i). İlk sürümde saç fiziksiz de kabul edilebilir.

### Çantalar

Çantanın tipi `DA_Item` içinde tutulur. Tip, çantanın bağlandığı yeri ve gerekiyorsa karakterin duruşunu belirler.

| Tip | Bağlantı | Not |
|---|---|---|
| **Omuz çantası** | Omuz veya üst kol socket'i | Kol hareketinde vücuda girmemesine dikkat edilmeli |
| **El çantası** | El socket'i | Parmakların tutuş pozu gerekir |
| **Çapraz çanta** | Skeletal Mesh | Askı gövdeyi sardığı için giysi gibi bükülür |
| **Sırt çantası** | Sırt socket'i veya Skeletal Mesh | Askılar giysilerin üstünde durmalı |

İlk sürümde tek çanta bölgesi yeterli. Socket'ler vücut modeline bağlı olduğu için konum ayarları `DA_CharacterBody` ile uyumlu tutulur.

## Aşamalar

### 1. Model hazırlığı

- [x] VRoid'de temel modeli oluştur
- [x] VRM4U'yu kur
- [x] Modeli Unreal'a aktar
- [ ] Vücut oranlarını sabitle (boy, beden)
- [ ] Yüz benzerliğini finalize et: perçem, ağız, kaşlar (en sona bırakıldı)

### 2. Teknik deneme

En riskli adım, sistemden önce doğrulanacak.

- [ ] VRM'i Blender'a al (VRM eklentisi gerekebilir)
- [ ] Tişört, şort ve ayakkabıyı vücuttan ayır
- [ ] Kıyafet çıkınca vücudun altının tam olduğunu kontrol et
- [ ] Parçaları aynı iskeletle Unreal'a geri al
- [ ] Leader Pose ile vücutla birlikte hareket ettiğini doğrula

### 3. Giydirme sistemi

- [ ] `DA_Item` ve `DA_CharacterBody`
- [ ] `OutfitComponent`
- [ ] `BP_DressUpCharacter`
- [ ] Bölge engelleme kuralları

### 4. Vücut maskesi

- [ ] Bölge maskesi dokusunu hazırla
- [ ] MToon materyaline bölge gizleme ekle
- [ ] Maskenin başka bir VRoid modelinde çalıştığını test et

### 5. İlk içerik

- [ ] 3 giysi ve 1 aksesuar (gözlük) ile tak-çıkar testi
- [ ] Renk seçenekleri
- [ ] Saçı ayır, 2 saç modeliyle değiştirme testi
- [ ] 1 omuz çantası ve 1 el çantasıyla tip testi

### 6. Sahne

- [ ] Boş level ve sabit kamera
- [ ] Sıcak ışık kurulumu, yüzdeki gölge sorununu çöz
- [ ] Idle animasyon

### 7. Arayüz

- [ ] Bölge sekmeleri ve ikonlu kıyafet listesi
- [ ] Otomatik ikon üretimi
- [ ] Sıfırlama ve "Bitir" düğmeleri

### 8. Finalize ekranı

- [ ] Poz ve kamera yaklaşması
- [ ] Fotoğraf çekme
- [ ] Kişisel mesaj ve tekrar oynama

### 9. İçerik ve cila

- [ ] Toplam 15-20 kıyafet parçası
- [ ] Referans görsellerdeki parçalar: vatkalı siyah kolsuz üst, yüksek bel jean, siyah pileli pantolon, siyah blazer, tokalı kemer, gümüş kolye
- [ ] Kişisel dokunuşlar: onun gerçek kıyafetlerine benzeyen parçalar, en sevdiği renkler, gizli seçenekler
- [ ] Etek ve uzun ceket fiziği
- [ ] Ses, müzik, kıyafet değiştirme animasyonu

### 10. Teslim

- [ ] Paketleme
- [ ] Hedef bilgisayarda test

## Kıyafet kaynakları

- **VRoid Studio:** Kendi kıyafetleri, doğal olarak en uyumlu seçenek
- **Blender script:** Vücuda oturan basit parçalar ve renk varyasyonları
- **Fab, Sketchfab, Booth:** Gösterişli parçalar, her birinin lisansı kontrol edilmeli
- **Marvelous Designer:** En kaliteli sonuç, ama elle dikiş gerektirir
- **Meshy, Tripo:** Çanta, şapka gibi aksesuarlar

## Riskler

| Risk | Etki | Önlem |
|---|---|---|
| Parçalar Unreal'a aynı iskeletle dönmeyebilir | Giydirme sisteminin temeli bozulur | 2. aşamada sistemden önce test et |
| Vücut oranları sonradan değişir | Kıyafetler yeniden uydurulur | Oranları erken sabitle, uydurmayı Blender'da script ile yap |
| Maske başka modelde uymayabilir | Model değişince maske yenilenir | 4. aşamada test et |
| MToon'da maskeleme sorun çıkarabilir | Bölge gizleme çalışmaz | Yedek: Vücudu materyal bölümlerine ayır |
| Katmanlı giysiler iç içe girebilir | Görsel kusur | Bölge engelleme ve parça bazlı uydurma |
| Saç kemikleri modele göre değişebilir | Saç fiziği çalışmaz | İlk sürümde fiziksiz başla, gerekirse Copy Pose kullan |
| Çanta vücuda girebilir | Görsel kusur | Tip bazlı socket ayarı ve idle pozda kontrol |
| Hedef bilgisayar zayıf olabilir | Düşük performans | Teslimden önce test et |
