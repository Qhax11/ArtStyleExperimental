# Giydirme Oyunu Yol Haritası

Son güncelleme: 2026-11-05

## Projenin amacı

Proje en temelinde bir **giysi giydirme oyunu**. Oyuncu, sabit kamerada duran anime tarzı karakteri arayüzden seçtiği kıyafet, saç ve aksesuarlarla giydirir, kombinini tamamlayıp finalize eder.

Oyun cozy bir hava taşır ve hediye olarak yapılıyor, satılmayacak. Karakter hediye edilen kişinin anime hali olduğu için benzerlik ve kişisel dokunuşlar, içerik sayısından daha önemli.

**Karakter yerinde durur.** Yalnızca hafif bir idle oynar (nefes alma, göz kırpma) ve finalde poz verir. Bu yüzden saç ve kumaş fiziği, hareket animasyonları ve hareket halinde kumaş kontrolü kapsam dışıdır.

**Oyuncunun değiştirebilecekleri:**

- **Giysiler:** Üst, alt, elbise, dış giyim, çorap, ayakkabı
- **Saç:** Farklı saç modelleri ve renkleri
- **Aksesuarlar:** Gözlük, küpe, kolye, şapka
- **Çantalar:** Tipine göre omuzda, elde, çapraz veya sırtta

## Yeni oturum için devam notu

**Sıradaki iş:** Aşama 3, giydirme sistemi. Aşama 2'nin tamamlanma ölçütü karşılandı. Dış kıyafet uydurmaya başlamadan önce Şamil'den vücut oranlarının son hali teyit edilmeli.

**Çalışma kuralları:**

- Şamil ile Türkçe konuş. Yeni bir konuya girmeden önce planı konuş, yön kararlarını ona bırak.
- Planlama sırasında sormadan ortam kontrolü yapma, gerekeni sor.
- Dosya indirmeden önce dosya adı, kaynak ve boyutu belirtip onay al.

**Önceki oturumdan kalanlar:**

- `evrar_test` aktörü, `Lvl_ThirdPerson` içine kaydedilmeden konulmuştu. Editör sonradan kapandıysa gitmiş olmalı, level'da varsa silinmeli.
- Plugin'in geçici kopyası `C:\v4u_tmp` silinemedi. Şamil elle silebilir.
- `Plugins/`, `SourceAssets/` ve `ROADMAP.md` commit edilmedi. `.uproject` dosyasında da commit edilmemiş MCP plugin değişikliği var.

**Bilinen araç notları:**

- Parça hattı: `SourceAssets/Scripts/split_vrm.py` VRM'i böler, `export_parts_fbx.py` FBX üretir, `SkeletalMeshTools.import_file` ile `SKEL_evrar` üzerine alınır. Materyaller ayrıca atanır.
- Leader Pose için parçanın kemik açıları ve ölçeği vücutla aynı olmalı. VRM4U'da kemik açıları sıfır, ölçek 1'dir. `vroid_fbx_common.py` bunu sağlar. Eşleşmezse parça görünmez olur veya huni gibi büzülür.
- Örnek model kıyafet hattı: örnek modeli aç, menüden "Bulk export worn items as XWear" ile `.xwear` al. Dress-up'ta `evrar`'ı aç, `Cloth`'u gizle, kıyafeti ekle, "Maintain Costume Shape" uygula, otomatik mesh silmeye "No" de, VRM dışa aktar. `retarget_costume_fbx.py` kıyafeti vücut iskeletine taşır. Materyaller için aynı VRM ayrıca VRM4U ile aktarılır.
- `import_file` aynı adlı asset'in üzerine yazmaz, önce silmek gerekir.
- Tam vücut için iki şey gerekir: VRoid dışa aktarmada "Delete Transparent Meshes" kapalı olmalı, ayrıca vücut dokusunun alpha'sı kaldırılmalı (`make_body_texture_opaque.py`, sonuç `T_Body_Opaque`). VRoid kıyafet altını alpha ile de keser, renkler ve siyah üst dokuda durur. Doku değişimi `MI_N00_000_00_Body_00_SKIN__Instance_` ve `_outline` materyallerinde yapıldı.
- VRM4U'nun `destination_package_path` değeri beklenen klasöre değil, bir üstüne yazıyor. Aktarımdan sonra konumu kontrol et.
- VRM aktarımı: `VRM4UAssetToolset.import_vrm_model`, `VRMIMT_MToon`. Asset'ler kaydedilmemiş gelir, `save_assets` gerekir.
- `CaptureViewport`: `captureTransform` ve `annotations` boş geçilemez. Çıktı dosyaya düşer, `returnValue.image.data` base64'ten PNG'ye çözülür.
- VRoid'i computer use ile kullanırken erişim adı `VRoidStudio 2.16.0`. `open_application` ikinci kopya açtı, pencereyi öne almak için PowerShell `AppActivate` kullanıldı. Slider'lar sürüklenerek ayarlanıyor, renk kutularına yazılabiliyor.

## Mevcut durum

- UE 5.8, `ArtStyleExperimental` projesi, içerik `/Game/DressUp/` altında
- VRM4U plugin'i `Plugins/VRM4U` içinde kurulu (5.8 sürümü, v1.2026.10.17)
- Model VRoid Studio ile hazırlandı (`evrar.vroid`, Şamil kaydetti), benzerlik ayarları henüz bitmedi
- VRM dosyası: `SourceAssets/VRoid/evrar.vrm`
- Model `/Game/DressUp/Character` altına MToon materyalleriyle aktarıldı (ana mesh: `SK_evrar`, iskelet: `SKEL_evrar`)
- Tişört, şort, ayakkabı ve saç ayrıldı, test asset'leri `/Game/DressUp/Items` altında (`SK_*_Test`). Test Blueprint'i: `/Game/DressUp/Core/BP_LeaderPoseTest`
- **Tam vücut:** `SK_evrar_full` (`SKEL_evrar_full`, kaynak `SourceAssets/VRoid/evrar_full.vrm`). Parçalar ve test pozu bu iskelete bağlı. Kıyafetler ise `evrar.vrm`'den geliyor, çünkü tam vücut dosyasında kıyafetler de fazladan gizli geometri taşıyor.
- **Geçici durumlar:** `SK_evrar_full` hâlâ kıyafet bölümleri içeriyor, Blueprint bunları gizliyor. VRM4U asset'leri `/Game/DressUp` köküne düştü, klasöre taşınmalı. Eski `/Game/DressUp/Character` artık kullanılmıyor, silinmesi Şamil'e sorulmalı.
- Yüzdeki tırtıklı gölge biliniyor, ışık kurulurken çözülecek

## Kararlar

| Konu | Karar | Neden |
|---|---|---|
| Karakter | VRoid, anime tarzı | Benzerlik ve kıyafet uydurma daha kolay, cozy hava kendiliğinden geliyor |
| Aktarım | VRM → VRM4U, MToon | Toon görünümü ve yüz ifadeleri hazır geliyor |
| Hareket | Sadece hafif idle ve final pozu | Oyunda karakter yürümüyor |
| Fizik | Yok | Karakter yerinde durduğu için gereksiz |
| Giysiler | Child Skeletal Mesh + Leader Pose | Kıyafet vücudun pozunu ve idle'ını otomatik alır |
| Aksesuarlar | Socket'e bağlı Static Mesh | Bükülmeleri gerekmiyor |
| Saç | Ayrı, değiştirilebilir bölge | Saç modeli oyuncunun seçimlerinden biri |
| Çantalar | Tipine göre bağlantı noktası | Her çanta tipi vücutta farklı yerde durur |
| Vücut gizleme | Bölge maskesi dokusu | Mesh'i parçalamak gerekmiyor |
| Temel katman | Vücut dokusundaki siyah üst ve şort | Çıplak başlangıcın teknik faydası yok, karakter de gerçek birine dayanıyor |
| Kıyafet tarzı | Serbest | 90'lar tarzı yalnızca varsayılan avatar için kullanıldı, kıyafetleri sınırlamaz |
| Kıyafet kaynağı | Önce VRoid | Ücretsiz ve vücuda en yakın, bkz. Kıyafet kaynakları |
| Mantık | Blueprint | MCP ile hızlı ilerliyor, C++ gerektiren bir ihtiyaç yok |

## Mimari

```text
BP_DressUpCharacter
└─ BodyMesh (ana iskelet, idle ve poz)
   ├─ Hair                                    → Skeletal Mesh (Leader Pose)
   ├─ Top, Bottom, Dress, Outer, Socks, Shoes → Skeletal Mesh (Leader Pose)
   ├─ Glasses, Earrings, Necklace, Hat        → Static Mesh (socket)
   └─ Bag                                     → Çanta tipine göre socket veya Skeletal Mesh
```

Her bölge için baştan boş bir component bulunur. Takmak mesh atamak, çıkarmak mesh'i boşaltmak demektir.

### Veri ve mantık

**`DA_Item`:** Her kıyafet ve aksesuar için bir kayıt. Yeni parça eklemek kod gerektirmez.

| Alan | Açıklama |
|---|---|
| Id, DisplayName, Icon | Kimlik ve arayüz bilgisi |
| Slot | Takıldığı bölge |
| SkeletalMesh veya StaticMesh | Parçanın mesh'i |
| Socket, Offset | Yalnızca katı parçalar için |
| ColorOptions | Seçilebilir renkler |
| HiddenBodyRegions | Altında gizlenen vücut bölgeleri |
| BlockedSlots | Engellediği bölgeler (elbise üst ve altı engeller) |
| BagType | Yalnızca çantalar için |

**`DA_CharacterBody`:** Vücut mesh'i, idle, final pozu, bölge maskesi ve socket konum ayarları. Model değişince burası değişir, sistem aynı kalır.

**`OutfitComponent`:** `Equip`, `Unequip`, `GetEquipped`, `ResetToDefault`, kombin kaydetme ve yükleme. Engelleme kuralları ve vücut gizleme burada çalışır. Arayüz yalnızca bununla konuşur, yani hiçbir mantık arayüze bağlı olmaz.

### Vücut gizleme

Maske dokusu vücudu bölgelere ayırır: Göğüs, karın, kalça, üst kol, alt kol, uyluk, baldır, ayak. Kıyafet takılınca `HiddenBodyRegions` listesindeki bölgeler materyalde gizlenir.

Yedek plan: MToon'da maskeleme sorun çıkarırsa vücut, Blender'da materyal bölümlerine ayrılır.

### Saç

- Saç, vücuttan ayrı bir mesh olarak kendi bölgesinde durur. Modelde saç ayrı materyallerle geliyor (`Hair`, `HairBack`).
- Şapka ile çakışan saçlar `DA_Item` kurallarıyla yönetilir.
- Renk değişimi materyal parametresiyle yapılır.

### Çantalar

Çantanın tipi `DA_Item` içinde tutulur. Tip, bağlantı yerini ve gerekiyorsa duruşu belirler.

| Tip | Bağlantı | Not |
|---|---|---|
| **Omuz çantası** | Omuz veya üst kol socket'i | İdle pozda vücuda girmemeli |
| **El çantası** | El socket'i | Parmaklar için tutuş pozu gerekir |
| **Çapraz çanta** | Skeletal Mesh | Askı gövdeyi sardığı için giysi gibi bükülür |
| **Sırt çantası** | Sırt socket'i veya Skeletal Mesh | Askılar giysilerin üstünde durmalı |

İlk sürümde tek çanta bölgesi yeterli.

### Klasörler

```text
/Game/DressUp/Character   Vücut ve VRM4U asset'leri
/Game/DressUp/Core        BP_DressUpCharacter, OutfitComponent, veri türleri
/Game/DressUp/Items       Parçalar: Hair, Tops, Bottoms, Dresses, Outer, Shoes, Accessories, Bags
/Game/DressUp/Data        DA_Item ve DA_CharacterBody kayıtları
/Game/DressUp/UI          Widget'lar
/Game/DressUp/Maps        LVL_DressUp
SourceAssets/             Unreal dışı kaynaklar: VRM, Blender dosyaları
```

## Blender'ın görevi

Blender, Şamil'in açmasına gerek olmadan Python script'leriyle arka planda çalışır.

1. **Parçalara ayırma:** Modelin içindeki kıyafetleri ve saçı, kemik bağlarını koruyarak ayrı dosyalara ayırır.
2. **Vücudu tamamlama:** Kıyafet altında eksik yer varsa VRoid'den alınan kıyafetsiz vücudu kullanır.
3. **Uydurma:** Başka bedenden veya dışarıdan gelen parçayı onun bedenine oturtur, vücudun kemik bağlarını aktarır.
4. **Basit üretim:** Atlet, tayt, çorap gibi vücuda oturan parçaları vücuttan türetir.

## Aşamalar

### 1. Model hazırlığı

- [x] VRoid'de temel modeli oluştur
- [x] VRM4U'yu kur
- [x] Modeli Unreal'a aktar
- [ ] Vücut oranlarını sabitle (boy, beden)
- [ ] Yüz benzerliğini finalize et: perçem, ağız, kaşlar (en sona bırakıldı)

Vücut oranları değişirse kıyafetler yeniden uydurulur, bu yüzden erken sabitlenmeli. Yüz değişiklikleri kıyafetleri etkilemez.

### 2. Teknik deneme

En riskli adım, sistemden önce doğrulanır.

**A. Mevcut parçaları ayırma**

- [x] Blender VRM eklentisini kur (v4.10.4, Blender 5.1.1)
- [x] `evrar.vrm` dosyasını Blender'a al
- [x] Tişört, şort, ayakkabı ve saçı kemik bağlarıyla ayır
- [x] Vücudu tek başına göster, kıyafet altında eksik var mı bak (göğüs ve üst kollarda delik var)
- [x] Tam vücudu VRoid'den al, Unreal'a aktar
- [x] Parçaları `SKEL_evrar` iskeletiyle Unreal'a aktar

**B. Unreal'da doğrulama**

- [x] Vücudu ve parçaları Leader Pose ile birleştir
- [x] Karakteri T-pozundan doğal bir poza al, parçaların birlikte geldiğini gör
- [x] Tek parçayı çıkarıp tekrar tak

**C. Örnek model kıyafeti**

- [x] Örnek modellerin kullanım şartlarını oku, Şamil'e özetle (Şamil onayladı; oyun satılmayacağı için uygun görüldü, satış düşünülürse yeniden okunmalı)
- [x] Örnek G'nin kapüşonlusunu Dress-up özelliğiyle onun modeline giydirmeyi dene (çalıştı, Unreal'da poz alıyor)
- [ ] Kıyafetin içinden taşan göğsü Aşama 4 vücut maskesiyle çöz. Test asset'leri: `/Game/DressUp/Items/SampleG/Parts`

**Tamamlanma ölçütü:** Bir model ve en az 4 ayrı parça, aynı iskelette birlikte poz alıyor, ayrıca bir örnek model kıyafeti için çalışan bir yol biliniyor. Bu olmadan Aşama 3'e geçilmez.

### 3. Giydirme sistemi

- [ ] Bölge listesi ve veri türleri
- [ ] `DA_Item` ve `DA_CharacterBody`
- [ ] `OutfitComponent`
- [ ] `BP_DressUpCharacter`
- [ ] Bölge engelleme kuralları

**Tamamlanma ölçütü:** Arayüz olmadan `Equip` ve `Unequip` çağrılarıyla parçalar değişiyor, elbise üst ve altı çıkarıyor.

### 4. Vücut maskesi

- [ ] Bölge maskesi dokusunu hazırla
- [ ] MToon materyaline bölge gizleme ekle
- [ ] `OutfitComponent` ile bağla
- [ ] Maskenin başka bir VRoid modelinde çalıştığını test et

**Tamamlanma ölçütü:** Uzun ve kısa kıyafette deri kumaştan dışarı taşmıyor, kıyafet çıkınca bölge geri geliyor.

### 5. İlk içerik

- [ ] 3 giysi ve 1 elbise
- [ ] 2 saç modeli
- [ ] Gözlük ve küpe
- [ ] 1 omuz çantası ve 1 el çantası
- [ ] Renk seçenekleri

**Tamamlanma ölçütü:** Her parça türü en az bir örnekle sistemde çalışıyor.

### 6. Sahne

- [ ] `LVL_DressUp`: Boş level, sabit kamera, karakter bir yanda
- [ ] Sıcak ışık kurulumu, yüzdeki gölge sorununu çöz
- [ ] Idle animasyon: Kaynağını Şamil ile seç (hazır animasyon veya Unreal'da elle)
- [ ] Oyun başlangıcında varsayılan kıyafet

### 7. Arayüz

- [ ] Bölge sekmeleri ve ikonlu parça listesi
- [ ] Otomatik ikon üretimi
- [ ] Renk seçimi
- [ ] Sıfırlama ve "Bitir" düğmeleri

### 8. Finalize ekranı

- [ ] Final pozu ve kamera yaklaşması
- [ ] Fotoğraf çekme
- [ ] Kişisel mesaj ve tekrar oynama

### 9. İçerik ve cila

- [ ] Toplam 15-20 parça (liste Şamil'den gelecek)
- [ ] Kişisel dokunuşlar: onun gerçek kıyafetlerine benzeyen parçalar, en sevdiği renkler, gizli seçenekler
- [ ] Ses, müzik, kıyafet değiştirme efekti
- [ ] Yüz benzerliğinin son ayarları

### 10. Teslim

- [ ] Paketleme
- [ ] Hedef bilgisayarda test

## Kıyafet kaynakları

Önce VRoid, eksik kalanlar için diğerleri.

| Parça | Kaynak | Yapan |
|---|---|---|
| Temel üst, alt, elbise, ayakkabı | VRoid'in kıyafet sekmesi | Claude dışa aktarıp ayırır |
| Hazır kostümler | Örnek modeller, Dress-up (`.xwear`) | Claude ayırır veya uydurur |
| Saç modelleri | VRoid'in hazır saçları | Claude dışa aktarıp ayırır |
| Renk ve desen farkları | Aynı parçaların dokuları | Claude |
| Atlet, tayt, çorap | Vücuttan türetme | Claude, Blender'da |
| Gözlük, küpe, kolye | Sketchfab, Fab veya basit üretim | Claude uydurur, seçim birlikte |
| Çantalar | Fab, Sketchfab, Meshy, Tripo | Claude uydurur, seçim birlikte |
| Özel, gösterişli parçalar | Fab, Sketchfab, Booth | Claude uydurur, sonuç parçaya göre değişir |

İddialı kıyafetler sıfırdan modellenmez, çünkü kalitesi düşük olur. Dış kaynaklı her parçanın lisansı kontrol edilir.

**Örnek modellerde adaylar:** G (kapüşonlu), C (fermuarlı ceket), P (takım ceketi), A (hırka), O (siyah elbise), M (mavi-beyaz elbise).

## Açık sorular

| Soru | Kim | Ne zaman |
|---|---|---|
| Vücut oranları son halinde mi? | Şamil | Dış kıyafet uydurmadan önce |
| Kıyafet için bütçe var mı? | Şamil | Aşama 5 öncesi |
| 15-20 parçalık kıyafet listesi | Şamil | Aşama 5 öncesi |
| Oyun hangi bilgisayarda oynanacak? | Şamil | Aşama 10 öncesi |
| Oyun sürpriz mi olacak? | Şamil | Yüz finalize edilmeden |

## Riskler

| Risk | Etki | Önlem |
|---|---|---|
| Parçalar Unreal'a aynı iskeletle dönmeyebilir | Giydirme sisteminin temeli bozulur | Aşama 2'de sistemden önce test et |
| Örnek model kıyafetleri alınamayabilir veya şartlar uygun olmayabilir | Kıyafet çeşitliliği azalır | VRoid'in kıyafet sekmesi ve dış kaynaklar |
| Başka bedenden gelen kıyafet oturmayabilir | Her parça elle düzeltme ister | Blender'da uydurma ve tek poz için düzeltme |
| Vücut oranları sonradan değişir | Kıyafetler yeniden uydurulur | Oranları erken sabitle, uydurmayı script ile yap |
| Maske başka modelde uymayabilir | Model değişince maske yenilenir | Aşama 4'te test et |
| MToon'da maskeleme sorun çıkarabilir | Bölge gizleme çalışmaz | Vücudu materyal bölümlerine ayır |
| Katmanlı giysiler iç içe girebilir | Görsel kusur | Bölge engelleme ve parça bazlı uydurma |
| Hedef bilgisayar zayıf olabilir | Düşük performans | Teslimden önce test et |
