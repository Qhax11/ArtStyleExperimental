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

**Sıradaki iş:** Pastel stüdyo, ikonlar ve sekmeli arayüz hazır. Şamil fareyle denemeli. Sırada "Bitir" düğmesi ve Aşama 8. Yüz ve ten rengi sona bırakıldı.

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
- `import_file` aynı adlı asset'in üzerine yazmaz, önce silmek gerekir.
- VRM4U kaynaktan derleniyor. `VrmAssetListThumbnailRenderer.cpp` satır 257'deki renk değerlerine `f` eklendi (double uyarısı hata sayılıyordu). Eklenti güncellenirse tekrar gerekebilir.
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
- [ ] Renk seçenekleri (alan var, mantık yok; Aşama 5)
- [ ] `OnOutfitChanged` henüz test edilmedi, arayüz bağlanınca doğrulanacak. Fonksiyonun adı `GetEquippedItem` oldu, testte çalıştı.

**Tamamlanma ölçütü:** Arayüz olmadan `Equip` ve `Unequip` çağrılarıyla parçalar değişiyor, elbise üst ve altı çıkarıyor. Karşılandı; test sürücüsü `/Game/DressUp/Core/Test/BP_OutfitTestDriver`.

### 4. Vücut maskesi

- [x] Vücudu bölgelere ayır (`SK_BodyRegions`)
- [x] `OutfitComponent` ile bağla (`RefreshBodyVisibility`)
- [x] Kayıtlara `HiddenBodyRegions` yaz
- [x] Tişört, şort ve kapüşonluyla önden test et, kapüşonluyu arkadan ve yandan da kontrol et
- [x] Beldeki çentik düzeltildi (2026-11-06): kemik ağırlığına göre `Hips` bölgesi şort bel bandının üstüne çıkıyordu. `split_body_regions.py` artık `Hips` yüzlerini vücut boyunun 0.95/1.59 oranında kesiyor, üstü `Belly`'ye gidiyor. Yeni alt giysi daha alçak belliyse bu oran düşürülür.
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
- [x] Idle animasyon: Mixamo'dan iki döngüsel bekleme (`SourceAssets/Mixamo/Idle_A.fbx` 8.3 sn, `Idle_B.fbx` 16.6 sn), `SourceAssets/Scripts/export_mixamo_fbx.py` ile karaktere aktarıldı (iki iskelet de T-pozda; kemik başına dünya dönüş farkı, kalça boy oranıyla). `DA_Body_evrar.IdleAnim` = `/Game/DressUp/Core/Anim/Idle/SK_Idle_A_Anim`. B'yi denemek için aynı alanı değiştir.
- [ ] Göz kırpma: VRoid yüzü morph target ile çalışıyor, kodla rastgele aralıklarla eklenecek.
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
- [ ] "Bitir" düğmesi

### 8. Finalize ekranı

- [ ] Final pozu ve kamera yaklaşması
- [ ] Fotoğraf çekme
- [ ] Kişisel mesaj ve tekrar oynama. Mesaj, giyilen kıyafete uyan mesajlar listesinden rastgele seçilir; mesajları Şamil yazar.

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
