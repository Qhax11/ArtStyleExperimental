# Giydirme Oyunu Yol Haritası

Son güncelleme: 2026-11-08

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

**Sıradaki iş:** Giydirme, sahne, arayüz, bekleme animasyonları ve final ekranı (poz, mesaj, fotoğraf, tekrar) hazır. Kıyafetler iç içe geçmeye karşı düzeltildi. Şamil'in gerçek mesajları ve parça listesi bekleniyor (Aşama 9). İçerik, sahne cilası, yüz ve göz kırpma en sona.

**C++ yapısı:** `DressUpTypes` (slot ve bölge enum'ları, kombin yapısı), `DressUpData` (`UDressUpItem`, `UDressUpBody`, `UDressUpCatalog`), `UOutfitComponent` (takma, çıkarma, engelleme, vücut gizleme, renk, kombin kaydetme), `ADressUpCharacter`, `ADressUpGameMode` ve `ADressUpPlayerController`, `DressUpPanel` (arayüz taban sınıfları). Parçalar `DA_Catalog` içinde listelenir. Widget'lar yalnızca düzeni tutar; `Btn`, `Label`, `List`, `Colors`, `ResetBtn` adları C++'a bağlıdır. `BP_DressUpGM` ana menü level'ı kullandığı için duruyor, `ADressUpGameMode`'dan türüyor. Yeni C++ sınıfı veya alan eklemek editörü kapatıp derlemeyi gerektirir.

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
- **Kıyafet hattı (her yeni kıyafet buradan geçer, Şamil'in kuralı):** FBX'i Unreal'e doğrudan alma. Önce `fix_cloth_fbx.py` ile işle:
  `blender parts_full/evrar_full_parts.blend --background --python fix_cloth_fbx.py -- <in.fbx> VRoid/fixed/SK_<Parça>.fbx --vrm <kaynak.vrm> [--tuck-above CM --tuck CM]`
  Betik iki şey yapar: kaynak VRM'deki dokusu tamamen saydam yüzleri siler (örnek kostümlerdeki gizli parçalar), vücuda yakın köşelere vücudun deri ağırlıklarını verir (3 cm'e kadar tam, 10 cm'den sonra kıyafetin kendi ağırlığı, arası karışım). Altı üstün içinden taşan giysiler için `--tuck-above`/`--tuck` bel bandını vücuda çeker (desenli şort: 88 cm üstü, 1.5 cm). Saç, gözlük ve şapka bu hattan geçmez. Sonra Unreal'e geçici adla al, eski mesh'in materyallerini slot adına göre kopyala, `DA_*.SkeletalMesh`'i bağla, eskiyi sil, yeniyi eski adına taşı. Ardından bekleme ve final pozlarında, en bol kıyafetlerle önden kontrol et.
- **VRMA hattı zemin sınırlaması:** `export_vrma_fbx.py` her karede ayak köşelerinin en alçağını hesaplar, zeminin altına inerse vücudu kaldırır (V işaretinde 4 cm'e kadar). Yeni VRMA hareketleri de bundan geçer.
- **Bekleme animasyonu hattı:** Mixamo FBX ("Without Skin") → `export_mixamo_fbx.py <in> <out> --arm-spread DEG`. Kolları omuzdan dışa açar; Idle A 4°, Idle B 7°. Yeni bekleme animasyonunu desenli şort ve elbiseyle kontrol et, el giysiye giriyorsa artır. Oyun kamerası önden baktığı için yandan küçük temas sorun değil.
- `import_file` aynı adlı asset'in üzerine yazmaz, önce silmek gerekir.
- VRM4U kaynaktan derleniyor. `VrmAssetListThumbnailRenderer.cpp` satır 257'deki renk değerlerine `f` eklendi (double uyarısı hata sayılıyordu). Eklenti güncellenirse tekrar gerekebilir.
- Tam vücut için iki şey gerekir: VRoid dışa aktarmada "Delete Transparent Meshes" kapalı olmalı, ayrıca vücut dokusunun alpha'sı kaldırılmalı (`make_body_texture_opaque.py`, sonuç `T_Body_Opaque`). VRoid kıyafet altını alpha ile de keser, renkler ve siyah üst dokuda durur. Doku değişimi `MI_N00_000_00_Body_00_SKIN__Instance_` ve `_outline` materyallerinde yapıldı.
- VRM4U'nun `destination_package_path` değeri beklenen klasöre değil, bir üstüne yazıyor. Aktarımdan sonra konumu kontrol et.
- VRM aktarımı: `VRM4UAssetToolset.import_vrm_model`, `VRMIMT_MToon`. Asset'ler kaydedilmemiş gelir, `save_assets` gerekir.
- `CaptureViewport`: `captureTransform` ve `annotations` boş geçilemez. Çıktı dosyaya düşer, `returnValue.image.data` base64'ten PNG'ye çözülür.
- VRoid'i computer use ile kullanırken erişim adı `VRoidStudio 2.16.0`. `open_application` ikinci kopya açtı, pencereyi öne almak için PowerShell `AppActivate` kullanıldı. Slider'lar sürüklenerek ayarlanıyor, renk kutularına yazılabiliyor.

## VRoid toplu içerik (2026-11-08)

VRoid'in tüm hazır parçaları oyunda: 235 parça, renk/desen varyantlarıyla 303 görünüm.
Üst 56 (82 görünüm), alt 37 (54), elbise 29 (33), ayakkabı 46 (59), yaka süsü 11 (18),
kol süsü 14 (15, yeni `Gloves` bölgesi), saç 37, kalın gözlük + 4 şapka.
Asset'ler `/Game/DressUp/Items/VRoid`, kayıtlar `/Game/DressUp/Data/VRoid/DA_*`,
ikonlar `/Game/DressUp/UI/Icons/VRoid`. Hepsi `DA_Catalog.AllItems` içinde.

**Hat (yeniden çalıştırılabilir, `SourceAssets/Scripts`):**
1. VRoid'den dışa aktarım: `vroid_multi_round.py` (dosyalar `SourceAssets/VRoid/presets`, `PROGRESS.md`).
2. `classify_presets.py` → `items.json`: materyaller vücuttaki konumuna göre bölgelere ayrılır,
   doku setine göre tekrarlar atılır, aynı mesh'li olanlar varyant olur.
3. `make_jobs.py` → `jobs.json`; `build_items.py` (Blender, tek oturumda tüm VRM'ler):
   ayırma + iskelete taşıma + **kıyafet hattı** (saydam yüz silme, vücut ağırlıkları; fix_cloth ile aynı).
4. `extract_textures.py` (dokular, en fazla 1024), `render_icons.py` (Blender ikonları),
   `item_coverage.py` (gizlenecek vücut bölgeleri, ışın testi), `make_manifest.py`.
5. Unreal: `ue_import_items.py` (MCP betiği; manifest `Saved/DressUpImport` altından okunur).
- **Önemli:** VRoid dokuları Unreal'da `TMGS_NoMipmaps` + `TC_BC7` olmalı. Mipmap'li dokuda
  VRM4U MToon çok düşük mip seçiyor, kıyafet bulanık görünüyor.
- **Varyantlar:** `UDressUpItem.Variants` (renk örneği + slot başına materyal). Arayüzde son seçilen
  parçanın varyantları renk kutularının yerine çıkar (`SetSlotVariant`, kayda da yazılır).
- **Arayüz:** parça listesi koddan `ScrollBox` içine alınır (`WrapListInScrollBox`).
- **Arayüz renkleri:** Beyaz yalnızca kıyafetlerde ve beyaz renk düğmesinde kalır (Şamil, 2026-11-08), beyaz ikonlar kutuda kaybolmasın diye. Kutu ve çip renkleri `DressUpStyle` içinde, panel zemini `WBP_DressUp` içinde. Seçili renk düğmesi koyu halka alır ve büyür (`UDressUpColorButton::RefreshSelected`).
- **Sıralama:** Sekme içi sıra `DA_Catalog.AllItems` sırasıdır. Benzer parçalar ikonlara bakılarak art arda dizildi; liste `SourceAssets/VRoid/presets/catalog_order.py` içinde. Yeni parça eklenince oraya da yazılmalı, betik eksik parçada durur.
- **İsimler:** Parça isimleri `SourceAssets/VRoid/presets/catalog_names.py` içinde. `ue_import_items.py` manifest'teki numaralı adları yazar, yeniden aktarımdan sonra isimler bu listeden tekrar uygulanmalı.
- **Döndürme ipucu:** `WBP_DressUp` içinde `RotateHint` (sağ alt, tıklamaları geçirir, panelle birlikte gizlenir). İkon `SourceAssets/Scripts/make_rotate_icon.py` ile çizilir.
- **Derleme:** Modül `SlateCore`'a bağlıdır (`FButtonStyle`).
- **VRoid yükseltmesi (2026-11-10):** VRoid, ayakkabı giydirince bütün modeli taban kalınlığı kadar
  (0,1–3,1 cm) yükseltip öyle dışa aktarıyor. `build_items.py` her parçayı kaynağının kalça farkı kadar
  indirir. Düzeltilmeden önce üstlerin kolları dışa açılıyor, göğüs kumaşı delip çıkıyordu.
- **Ayakkabılar:** VRoid ayakkabı içinde ayağı bilekten öne eğiyor (38 VRM'de 7,8°, 3'ünde 6–6,3°,
  5'inde 0). Hat ayakkabıyı düz ayağa çevirir, ayağa yakın yüzeyleri sıklaştırıp derinin 2 mm dışına
  iter. Oyunda `UDressUpItem.SoleHeight` kadar karakter yükselir, `FootPitch` kadar ayak eğilir
  (`UDressUpAnimInstance`; gövde animasyonları artık `PlayBodyAnimation` ile bu sınıftan oynar).
  `item_coverage.py` ayakkabıda derinin hemen altındaki yüzeyi de örtü sayar.
- **Kontrol betikleri:** `check_sleeves.py`, `sleeve_offset.py`, `render_fit.py` (Blender'da kollar
  inik görüntü).
- **Oyuncu adı:** Başlat'ta bir kez sorulur (`WBP_NamePrompt`), `DressUpSettings` kaydında saklanır,
  ESC menüsünde "İsmi değiştir". Ekranın üstünde `WBP_DressUp` içindeki `NameHud` gösterir
  (karaktere bağlı değil, panelle gizlenir). Test: `DressUpForgetName`.
- **Kıyafet sesleri:** `SourceAssets/Scripts/make_sfx.py` (numpy ile sentez) her sekme için giyme ve çıkarma
  sesi üretir (`SourceAssets/Audio/sfx`, dinleme sayfası `preview.html`). `ue_import_sfx.py` editörde
  `py` komutuyla `/Game/DressUp/Audio/SFX`'e alır, `SC_Effects`'e bağlar. Çalma: `DressUp::PlaySound`
  (`DressUpSound.h`). Arayüz: `UI_Tab` (sekme ve duruş), `UI_Color` (renk), `UI_Click` (diğer düğmeler),
  `Finish` (Bitir), `Photo` (fotoğraf).
- **Döndürme ipucu nabzı:** `UDressUpPanel::PulseRotateHint`, 7 sn'de bir 1 sn boyunca %15 büyür
  (`HintPulseInterval/Duration/Growth`).
- **Müzik:** "Lofi Hip Hop Loop" (omfgdude, OpenGameArt, CC0; `SourceAssets/Audio/music/SOURCE.txt`).
  `ue_import_music.py` ile `/Game/DressUp/Audio/Music/MUS_Lofi` (döngü, `SC_Music`).
  `UDressUpSettingsSubsystem::StartMusic` başlatır; sahne değişince kesilmez, duraklatmada da çalar.
- **Ceketler (katmanlı, 2026-11-11, deneme; katalogdan çıkarıldı):** Üç ceket az kaldı ve hangi üstün
  hangi cekete uyduğu arayüzde görünmüyordu; daha çok ceket gelince açılacak (asset'ler duruyor,
  `catalog_order.py` RETIRED). Açarken: arayüzde uyumsuz üstleri belli et. VRoid'de ayrı ceket kategorisi yok; ceketler üstün
  içindeki gömlekle tek parça, ama materyallere ayrılıyor. `Outer_046` (bej trençkot), `Outer_028`
  (açık krem blazer), `Outer_025` (gri hırka): kaynak üstün yalnızca dış materyalleri, `build_items.py`
  `"outer": true` ile vücuttan `OUTER_LIFT`/`OUTER_MIN` kadar dışarı alınır. "Ceket" sekmesi (`Outer`
  yuvası) üstü çıkarmaz, üstüne giyilir. Gömlek ve bluzla iyi; geniş kısa kollu tişörtün kolu omuzda
  taşıyor (tişörtün kendi kol bükülmesi). Malzeme: kaynak üstün MI'ları.
  Sığmayan üstler: `check_layers.py` her ceket-üst/elbise çiftini kollar inik ölçer; ceketin örttüğü
  yerde üstün %18'den fazlası dışarıdaysa çakışır. Liste ceketin `ClashingItems` alanında; çakışan
  parça giyilince diğeri çıkar (`UOutfitComponent::EquipInternal`, iki yönlü).
- **Renk çarpanı:** Bazı VRoid kıyafetleri beyaz dokuyla gelip rengini `baseColorFactor`'dan alıyor
  (gri hırka). Artık `extract_textures.py` bunu "color" olarak yazar, `ue_import_items.py` `mtoon_Color`'a
  koyar. Mevcut dört parça (Top_025, 026, 033, 034) elle düzeltildi.
- **Proje adı:** `DressUp.uproject`, ikon `Build/Windows/Application.ico`, açılış `Content/Splash/Splash.bmp`.
- **Test komutları:** `DressUpWear DA_X DA_Y:2 nopanel`, `DressUpGallery` (her kombinin fotoğrafı
  `Saved/Gallery`, liste logda "GALLERY n"). Galerideki arka çekim karakteri döndürmüyor, ön çekimler geçerli.
- MCP: 5 dakikayı aşan çağrı istemci tarafında kesilince editördeki MCP eklentisi kilitleniyor;
  editörü yeniden başlatmak gerekiyor. Betikleri ~4 dakikalık partilere böl.

**Yapılmayanlar:** örnek model kostümleri (A–Z, Dress-up/XWear yolu), dokuya boyalı VRoid çorapları
(34 adet; vücut dokusu farkından türetilebilir), kulak ve kuyruk.

## Mevcut durum

- UE 5.8, `DressUp.uproject` (hedefler `DressUp` / `DressUpEditor`, 2026-11-09'da adı değişti), içerik `/Game/DressUp/` altında.
  C++ modülü ve klasör adı `ArtStyleExperimental` olarak kaldı: modülü yeniden adlandırmak her asset'teki
  `/Script/ArtStyleExperimental` sınıf yolunu kırardı.
- Oyun ikonu `Build/Windows/Application.ico`, açılış görseli `Content/Splash/Splash.bmp`; ikisi de
  `SourceAssets/Scripts/make_app_icon.py` ile çizilir.
- VRM4U plugin'i `Plugins/VRM4U` içinde kurulu (5.8 sürümü, v1.2026.10.17)
- Model VRoid Studio ile hazırlandı (`evrar.vroid`, Şamil kaydetti), benzerlik ayarları henüz bitmedi
- VRM dosyası: `SourceAssets/VRoid/evrar.vrm`
- Model `/Game/DressUp/Character` altına MToon materyalleriyle aktarıldı (ana mesh: `SK_evrar`, iskelet: `SKEL_evrar`)
- Tişört, şort, ayakkabı ve saç ayrıldı, `/Game/DressUp/Items` altında (`SK_Top_Tshirt`, `SK_Bottom_Shorts`, `SK_Shoes_Sneakers`, `SK_Hair_Default`). G'nin kıyafetleri: `SK_Top_HoodieG`, `SK_Bottom_ShortsG`, materyalleri `Items/SampleG` altında.
- Testlikler `Core/Test` ve `Data/Test` altında. Eski karakter `/Game/DressUp/_Archive/Character_Old` altında, hiçbir şey kullanmıyor.
- **Tam vücut:** `SK_evrar_full` (`SKEL_evrar_full`, kaynak `SourceAssets/VRoid/evrar_full.vrm`). Parçalar ve test pozu bu iskelete bağlı. Kıyafetler ise `evrar.vrm`'den geliyor, çünkü tam vücut dosyasında kıyafetler de fazladan gizli geometri taşıyor.
- **Vücut asset'leri:** `/Game/DressUp/Character` altında (`Materials`, `Textures` alt klasörleri), `SK_BodyRegions` dahil.
- **Geçici durum:** `SK_evrar_full` hâlâ kıyafet bölümleri içeriyor, Blueprint bunları gizliyor.
- Yüzdeki tırtıklı gölge biliniyor, ışık kurulurken çözülecek

## Kararlar

| Konu | Karar | Neden |
|---|---|---|
| Karakter | VRoid, anime tarzı | Benzerlik ve kıyafet uydurma daha kolay, cozy hava kendiliğinden geliyor |
| Aktarım | VRM → VRM4U, MToon | Toon görünümü ve yüz ifadeleri hazır geliyor |
| Hareket | Sadece hafif idle ve final pozu | Oyunda karakter yürümüyor |
| Fizik | Yok | Karakter yerinde durduğu için gereksiz |
| Giysiler | Child Skeletal Mesh + Leader Pose | Kıyafet vücudun pozunu ve idle'ını otomatik alır |
| Aksesuarlar | VRoid'den gelen gözlük ve şapka Skeletal Mesh, dışarıdan gelecekler socket'e bağlı Static Mesh | VRoid aksesuarları kafa kemiğine bağlı gelip vücuda zaten oturuyor |
| Saç | Ayrı, değiştirilebilir bölge | Saç modeli oyuncunun seçimlerinden biri |
| Çantalar | Tipine göre bağlantı noktası | Her çanta tipi vücutta farklı yerde durur |
| Vücut gizleme | Vücudu bölge başına materyal bölümüne ayırmak | VRM4U materyaline ve eklentiye dokunmuyor, gerekirse maske dokusuna geçilebilir |
| Temel katman | Vücut dokusundaki siyah üst ve şort | Çıplak başlangıcın teknik faydası yok, karakter de gerçek birine dayanıyor |
| Kıyafet tarzı | Serbest | 90'lar tarzı yalnızca varsayılan avatar için kullanıldı, kıyafetleri sınırlamaz |
| Kıyafet kaynağı | Önce VRoid | Ücretsiz ve vücuda en yakın, bkz. Kıyafet kaynakları |
| Mantık | C++ (`Source/ArtStyleExperimental/DressUp`), görünüm Widget Blueprint | 2026-11-06'da Blueprint'ten taşındı: MCP ile Blueprint düzenlemek kırılgandı, git'te okunmuyordu, enum yoktu |

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

`split_body_regions.py` vücut mesh'ini her yüzün en güçlü kemiğine göre 10 bölgeye ayırır: `Chest`, `Belly`, `Hips`, `UpperArm`, `LowerArm`, `Hand`, `Neck`, `Thigh`, `Calf`, `Foot`. Sonuç `SK_BodyRegions`, her bölge bir materyal bölümü (`Region_*`). `RefreshBodyVisibility` tüm bölgeleri açar, sonra giyili parçaların `HiddenBodyRegions` listesindekileri `ShowMaterialSection` ile kapatır.

`SK_evrar_full` yalnızca yüzü gösterir ve lider iskelet olarak çalışır. Bölge sınırları poligon çözünürlüğündedir. Kısa kollu bir giysi `UpperArm` gizlememeli, yoksa kol ile kumaş arasında boşluk kalır.

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
- [x] Vücut oranlarını sabitle (Şamil onayladı, 2026-11-05)
- [ ] Yüz benzerliğini ve ten rengini finalize et: perçem, ağız, kaşlar (en sona bırakıldı)

Yüz ve ten için son adımda: `evrar_full.vrm` yeniden dışa aktarılır ("Delete Transparent Meshes" kapalı), `make_body_texture_opaque.py` çalışır, vücut ve yüz Unreal'da yenilenir. `HiddenBodySections` numaraları ve kafa boyutu değiştiyse saç oturuşu kontrol edilir.

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

- [x] Bölge listesi ve veri türleri (`PDA_Item`, `PDA_CharacterBody`; slot metin anahtarı, çünkü araçlar enum oluşturamıyor)
- [x] Parça kayıtları `/Game/DressUp/Data` altında (`DA_*`)
- [x] `BP_OutfitComponent`: `Equip`, `UnequipSlot`, `GetEquipped`, `ResetToDefault`, `OnOutfitChanged`
- [x] `BP_DressUpCharacter`
- [x] Bölge engelleme kuralları (iki yönlü: elbise üstü çıkarır, üst de elbiseyi çıkarır)
- [ ] Kombin kaydetme ve yükleme
- [x] Renk seçenekleri: ortak palet ve parça varyantları (renk kutuları, `SetSlotVariant`)
- [x] `OnOutfitChanged`: parça düğmeleri ve karakterin taban yüksekliği bunu dinliyor, çalışıyor.

**Tamamlanma ölçütü:** Arayüz olmadan `Equip` ve `Unequip` çağrılarıyla parçalar değişiyor, elbise üst ve altı çıkarıyor. Karşılandı; test sürücüsü `/Game/DressUp/Core/Test/BP_OutfitTestDriver`.

### 4. Vücut maskesi

- [x] Vücudu bölgelere ayır (`SK_BodyRegions`)
- [x] `OutfitComponent` ile bağla (`RefreshBodyVisibility`)
- [x] Kayıtlara `HiddenBodyRegions` yaz
- [x] Siyah elbise artık `Thigh` gizlemiyor (etek dizin üstünde bitiyor, bacak boşlukta kalıyordu).
- [x] Tişört, şort ve kapüşonluyla önden test et, kapüşonluyu arkadan ve yandan da kontrol et
- [x] Beldeki çentik düzeltildi (2026-11-06): kemik ağırlığına göre `Hips` bölgesi şort bel bandının üstüne çıkıyordu. `split_body_regions.py` artık `Hips` yüzlerini vücut boyunun 0.95/1.59 oranında kesiyor, üstü `Belly`'ye gidiyor. Yeni alt giysi daha alçak belliyse bu oran düşürülür.
- [x] Yeni `Ankle` bölgesi (2026-11-06): `Foot` bölgesi alçak ayakkabının ağzını izleyen eğimli bir çizgiyle bölündü (`split_body_regions.py` `FOOT_TOP`; önde 3.8 cm, topukta 8.8 cm). Mary Jane yalnızca `Foot`, spor ayakkabı `Foot` + `Ankle` gizler. Yeni ayakkabı eklerken ağzı bu çizgiden alçaksa bilekte boşluk, yüksekse ayak taşması olur; yakından kontrol et.
- [x] Çorap (`DA_Socks_O`) yalnızca `Thigh` ve `Calf` gizler; çorap bilekte bittiği için `Foot` gizlenmez.
- [x] VRM4U bazı parçaları `MI_VrmMToonOptLitTranslucent` ile alıyor; yarı saydam materyal gölge düşürmez. Çorabın materyali `MI_VrmMToonOptLitOpaque`'a (maskeli) geçirildi. Yeni parça eklerken üst materyale bak.
- [ ] Başka bir VRoid modelinde dene (script kemik adlarına bağlı, gerçek ihtiyaç doğarsa)

**Tamamlanma ölçütü:** Uzun ve kısa kıyafette deri kumaştan dışarı taşmıyor, kıyafet çıkınca bölge geri geliyor. Test pozunda karşılandı.

### 5. İlk içerik

- [x] Tişört, kapüşonlu, 2 şort ve siyah elbise (`DA_Dress_BlackO`, örnek O)
- [x] 2 saç modeli (`DA_Hair_Default`, `DA_Hair_Long`)
- [x] 2 ayakkabı ve çorap (`DA_Shoes_MaryJaneO`, `DA_Socks_O`)
- [x] Gözlük ve şapka (`DA_Glasses_Thin`, `DA_Hat_Cap`, VRoid aksesuar sekmesinden)
- [x] Renk değiştirme: `SetSlotColor` (kayıtlardaki `ColorOptions` henüz boş, parça değişince renk sıfırlanır)
- [ ] Küpe, kolye, çanta: VRoid'de yok. Şamil şimdilik VRoid'le devam dedi, `Earrings`, `Necklace`, `Bag` bölgeleri boş.

**Tamamlanma ölçütü:** Her parça türü en az bir örnekle sistemde çalışıyor. Çantalar ve küpe, kolye hariç karşılandı.

### 6. Sahne

- [x] `LVL_DressUp`: sabit kamera, karakter sağda. Başlangıcı C++ `ADressUpGameMode` / `ADressUpPlayerController` yapıyor (kamera, fare, arayüz).
- [x] Pastel stüdyo: krem zemin, pembe fon (`StudioBackdrop`), açık pembe halı (`StudioRug`), sıcak yönlü ışık. Materyaller `/Game/DressUp/Scene/MI_Studio_*`.
- [ ] Cozy dekor (en sona; yüzde gölge sorunu yok, Şamil 2026-11-06)
- [ ] Mekânlar (4 mevsim). Yeni yapı kuruldu, ilkbahar oyunda çalışıyor (2026-11-13):
  - Kod `Source/.../DressUp/Scene/`: `UDressUpScene` (mekân verisi), `UDressUpSceneSubsystem` (şu anki mekân, `OnSceneChanged`), `ADressUpSceneActor` tabanı ve yuva aktörleri: `ADressUpBackdrop` (fon resmi kamerayı doldurur, alttan sabit), `ADressUpGround` (gerçek zemin, kenarda kaybolur), `ADressUpPropSlot` (sabit konum, mekân sadece mesh verir; podyum da bir yuva), `ADressUpSceneEffect` (Niagara), `ADressUpLightRig` (güneş ve gök ışığı). Mekân değişince hepsi aynı karede değişir, yükleme yok.
  - Sahnede `Scene` klasöründe: Backdrop, Ground, Prop_* yuvaları, Effect, LightRig. Her aktörün "Preview Scene" alanı editörde o mekânı gösterir.
  - İçerik `Content/DressUp/Scene/Common` (M_SceneBackdrop, M_SceneGround, M_Prop, SM_Podium, SM_Stone) ve `Scene/Spring` (DA_Scene_Spring, T_Spring_Backdrop, MI_Spring_Ground, yaprak ve çiçek mesh'leri).
  - Koddaki bütün asset yolları Project Settings > Game > Dress Up'a taşındı (`UDressUpProjectSettings`, `DefaultGame.ini`). Kod klasörleri: Core, Game, Character, UI, Scene.
  - Kalan: ilkbahar Niagara yaprak efekti (editörde birlikte), zemin dokusu (ChatGPT), yaz/sonbahar/kış, final ekranında mekân cümlesi. `MI_Studio_*` eski stüdyodan kaldı, kullanılmıyor.
- [x] Idle animasyon: Mixamo'dan iki döngüsel bekleme (`SourceAssets/Mixamo/Idle_A.fbx` 8.3 sn; ikincisi `Idle_B.fbx` silindi), `SourceAssets/Scripts/export_mixamo_fbx.py` ile karaktere aktarıldı (iki iskelet de T-pozda; kemik başına dünya dönüş farkı, kalça boy oranıyla). `DA_Body_evrar.IdleAnim` = `/Game/DressUp/Core/Anim/Idle/SK_Idle_A_Anim`. B ("Salınım") Şamil'in isteğiyle 2026-11-08'de projeden silindi, A çok daha iyi görünüyordu.
- [x] VRoid'in resmî ücretsiz VRMA paketi (`VRMA_MotionPack`, 7 hareket) karakterin iskeletine alındı: `/Game/DressUp/Core/Anim/Motions/SK_VRMA_0X_Anim`. Yol: `SourceAssets/Scripts/export_vrma_fbx.py` (Blender VRM eklentisi VRMA'yı iskelete uygular, `prepare_armature` sonrası aynı deformasyon yeniden yazılır), FBX `import_animations=True` ile alınır. Hareketler: 01 tüm vücut, 02 selam, 03 V işareti, 04 ateş, 05 dönme, 06 model pozu, 07 çömelme. Kredi: "Character animation credits to pixiv Inc.'s VRoid Project". VRM4U'nun doğrudan aldığı deneme `/Game/DressUp/Core/Anim/VRMA` kendi iskeletinde, işe yaramıyor; editör kapalıyken diskten silinecek.
- [x] Oyun başlangıcı ve Sıfırla: kıyafetsiz, saçsız, iç çamaşırıyla (Şamil'in isteği, 2026-11-06). Katalogdaki `DefaultItems` boş.

### 7. Arayüz

- [x] İlk arayüz: `WBP_DressUp`, tek listede tüm parçalar, tekrar tıklayınca çıkarır (`WBP_ItemButton`)
- [x] Renk seçimi: son seçilen parçaya 6 renk (`WBP_ColorButton`), fareyle denenmedi
- [x] Sıfırlama düğmesi
- [x] Fareyle test: Şamil oyunda denedi, çalışıyor (2026-11-05). MCP Slate tıklaması oyun arayüzüne ulaşmıyor; otomatik testte `HandleClick` doğrudan çağrılır.
- [x] Sekmeler (Üst, Alt, Elbise, Ayakkabı, Saç, Aksesuar; `WBP_TabButton`), ikonlu kare kutular, pembe-krem pastel tasarım. Sekmeler katalogdaki `Tabs` alanından gelir, boşsa `DressUp::DefaultTabs()`. Parçası olmayan sekme gizlenir.
- [x] Parça ikonları otomatik: parça yeşil fon önünde çekilir, `SourceAssets/Scripts/make_icons.py` saydam 256px PNG'ye çevirir, `/Game/DressUp/UI/Icons` altına alınıp `UDressUpItem.Icon`'a bağlanır. Yeni parça eklenince aynı yol tekrarlanır.
- [x] Sekmeli arayüz fareyle denendi, çalışıyor (2026-11-06). Çorap `Alt` sekmesinde; sekmeler katalogda tanımlı.
- [x] Fareyle döndürme: sahneye basılı tutup yatay sürükleyince karakter yaw ekseninde döner, bırakınca en kısa yoldan kameraya bakan açısına yumuşakça döner (`ADressUpPlayerController::UpdateRotation`, ayarlar `RotateDegreesPerPixel` 0.4, `ReturnSpeed` 5). Giriş modu "Game and UI": arayüz tıklamaları döndürmez. Şamil fareyle denedi, çalışıyor (2026-11-06).
- [x] "Bitir" düğmesi ve "Duruş" çipleri (katalogdaki `IdleOptions`: Rahat, Dik duruş)

### 8. Finalize ekranı

- [x] Final pozu ve kamera yaklaşması: katalogdaki `FinalPoses`'tan rastgele biri (03 V işareti @3.0 sn, 06 model pozu @4.0), `HoldTime`'da donar. 02 selam çıkarıldı: başında çömeliyor, oyun yavaşlarsa o anda donuyordu (Şamil 2026-11-06). Kabarık etekle uyumsuz poz eklenirse pozlara kıyafet filtresi (`ExcludedItems`/`ExcludedSlots`) düşünülecek. Kamera `FinalCamera` etiketli `CameraActor_1`'e yumuşak geçer.
- [x] Fotoğraf: arayüzsüz ekran görüntüsü `%USERPROFILE%\Pictures\Dolap\Dolap_<tarih>.png`.
- [x] Mesaj ve tekrar oynama (`WBP_Final`): `Messages` içinden koşulu (`RequiredItems`, `RequiredSlots`) tutanlardan rastgele biri, hiçbiri tutmazsa koşulsuzlardan biri. Şu anki 5 mesaj "(Örnek)" yer tutucu; Şamil kendi mesajlarını `DA_Catalog > Finale > Messages`'a yazar. Köşede VRoid animasyon kredisi.
- [x] Test kısayolları (editör konsolu, oyun açıkken): `DressUpFinish`, `DressUpPhoto`, `DressUpReplay`.

### 9. İçerik ve cila

- [ ] Toplam 15-20 parça (liste Şamil'den gelecek)
- [ ] Kişisel dokunuşlar: onun gerçek kıyafetlerine benzeyen parçalar, en sevdiği renkler, gizli seçenekler
- [x] Ses, müzik, kıyafet değiştirme efekti (2026-11-11: sentez efektler, Lofi müzik)
- [ ] Yüz benzerliğinin son ayarları
- [ ] En son: göz kırpma (VRoid yüzü morph target ile çalışıyor, kodla rastgele aralıklarla). Şamil 2026-11-06: en sona.

### 10. Teslim

- [x] Paketleme (Şamil paketliyor; `Package.bat`, hedef `DressUp`)
- [ ] Hedef bilgisayarda test
- [ ] Vücut değişirse kıyafetleri uyarlama (Şamil, 2026-11-11: şimdilik kalsın). Yüz, saç, göz, ten
  değişikliği kıyafeti bozmaz; boy, göğüs, kalça, kol ve bacak kalınlığı bozar. Yollar: (1) VRoid'den
  130 civarı dosyayı yeniden dışa aktar, en doğru ama saatler sürer; (2) önerilen: eski ve yeni vücudu
  VRoid UV'leri üzerinden eşleyip her kıyafet köşesini altındaki deri kadar kaydır ("Surface Deform"
  mantığı, Blender'da dakikalar), kol ve göğüs ölçüm betikleriyle kontrol et, sorunlu bol parçaları
  (1) ile tamamla; (3) Unreal'da kemik boyu farkı kendiliğinden taşınır, kalınlık farkı taşınmaz;
  (4) kumaş simülasyonu, parça başına güzel ama 235 parça için yavaş.
- [ ] BOOTH'tan ek kıyafet (Şamil, 2026-11-11: en sona). Teknik: VRoid dokuları (VRoid kalıplarına
  desen) hatta doğrudan girer (VRoid'de evrar'a giydir, dışa aktar, `build_items.py`); XWear 3D kıyafetler
  daha detaylı ama lilToon ve yüksek poligon, uyarlama ister. Lisans: incelenen ücretsizlerin hepsi
  "ticari serbest, yeniden dağıtım yasak", oyuna gömme açıkça yazmıyor; ticari oyunda yalnızca "oyunda
  kullanım serbest" diyenler ya da yapımcıdan izin. Adaylar: ShopSlope near-future set
  (booth.pm/ja/items/1548851), よいどれ屋 maid texture (3248862), さめのワークス traveler (yayından kalkmış),
  VRoid Avatar Cafe apron (XWear, VN3, vroid.booth.pm/items/6235667), CLCT for DRESS (VRoid resmi, ticari
  serbest; muhtemelen VRoid hazırlarında zaten var, kontrol et). Ayrıca VRoid hazır kıyafetlerinin ticari
  oyundaki resmi kuralı netleştirilmeli.
- [ ] Lumen kararı (Şamil, 2026-11-10: şimdilik kalsın). Şablondan açık kaldı; toon materyalleri
  yüzünden karaktere katkısı az, yalnızca sahnenin seken ışığını veriyor. Ekran izleri kapalı
  (`DefaultEngine.ini`, beyaz kıyafetler zemine hale yapıyordu). Hedef bilgisayar zorlanırsa
  Lumen'i tamamen kapat ve ışığı yeniden kur: kapatınca gölge lacivert-siyah, sahne düz kalıyor;
  gökyüzü ışığı, gölge rengi ve SSAO ayarlanmalı.

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
| Bölge sınırı kıyafet kenarına uymayabilir | Küçük boşluk veya taşma | Parça bazlı `HiddenBodyRegions`, gerekirse bölge ekle |
| Katmanlı giysiler iç içe girebilir | Görsel kusur | Bölge engelleme ve parça bazlı uydurma |
| Hedef bilgisayar zayıf olabilir | Düşük performans | Teslimden önce test et |
