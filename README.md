# 🇹🇷 Battlefield 6 Türkçe Yama

<div align="center">

# BATTLEFIELD 6
### TÜRKÇE YAMA • gggg-unit Edition

**Battlefield 6 için Türkçe yama ve çevrimdışı kurulum aracı.**

![Version](https://img.shields.io/badge/S%C3%BCr%C3%BCm-V3.5-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge)
![Language](https://img.shields.io/badge/Dil-T%C3%BCrk%C3%A7e-red?style=for-the-badge)
![Installer](https://img.shields.io/badge/Kurulum-%C3%87evrimd%C4%B1%C5%9F%C4%B1-success?style=for-the-badge)

**[⬇️ TÜRKÇE YAMAYI İNDİR](https://github.com/gggg-unit/battlefield-6-turkce-yama/releases/latest)**

</div>

---

## 📖 Proje Hakkında

**Battlefield 6 Türkçe Yama — gggg-unit Edition**, Battlefield 6 için hazırlanan Türkçe yama dosyalarını desteklenen oyun platformlarına uygun şekilde kurmayı kolaylaştıran bir projedir.

Çevrimdışı kurulum aracı, oyun klasörünü kontrol eder, gerekli dosyaların bütünlüğünü doğrular ve mevcut dosyaları yedekleyerek kurulumu gerçekleştirir.

## ✨ Özellikler

- 🇹🇷 Türkçe yama desteği
- 🖥️ Windows üzerinde grafik arayüzlü kurulum
- 🎮 Steam, Epic Games, GOG, EA App ve Game Pass platform seçimi
- 📦 İnternet bağlantısı gerektirmeyen yerel dosya kurulumu
- 🛡️ Mevcut dosyaların otomatik yedeklenmesi
- 🔐 SHA-256 ile dosya bütünlüğü doğrulaması
- 📁 Oyun klasörünün kontrol edilmesi
- 🔄 Kurulum hatalarında değişiklikleri geri alma mekanizması
- ⚙️ PowerShell üzerinden komut satırıyla kurulum seçeneği

## ⬇️ İndirme

En güncel dağıtım paketini GitHub Releases bölümünden indirebilirsiniz.

### [📥 Battlefield 6 Türkçe Yama V3.5 — İndir](https://github.com/gggg-unit/battlefield-6-turkce-yama/releases/tag/full)

**Dağıtım dosyası:** `Battlefield-Turkce-Yama-v3.5.zip`

> **Önemli:** Kurulum için Releases bölümündeki dağıtım paketini kullanın. GitHub tarafından otomatik oluşturulan `Source code` arşivleri, kurulum için gerekli bütün yama dosyalarını içermeyebilir.

## 🛠️ Kurulum

1. Battlefield 6 oyununu tamamen kapatın.
2. Releases bölümünden en güncel ZIP paketini indirin.
3. ZIP arşivinin tamamını bir klasöre çıkarın.
4. `Kurulumu-Baslat.cmd` dosyasını çalıştırın.
5. Açılan kurulum penceresinde oyun platformunuzu seçin.
6. Battlefield 6'nın kurulu olduğu **ana oyun klasörünü** gösterin.
7. **Yedekle ve kur** düğmesine tıklayın.
8. Kurulum tamamlandıktan sonra oyunu başlatın.

### 📂 Doğru klasörü seçme

Kurulum aracı, seçilen ana oyun klasöründe şu dosyanın bulunmasını bekler:

`data\layout.toc`

`SP` klasörünü değil, oyunun ana kurulum dizinini seçmelisiniz.

## 🎮 Desteklenen Platform Seçenekleri

| Platform | Kurulum profili |
|---|---|
| Steam | Steam / Epic / GOG |
| Epic Games | Steam / Epic / GOG |
| GOG | Steam / Epic / GOG |
| EA App | EA / Game Pass |
| Xbox Game Pass | EA / Game Pass |

Kurulum aracı seçilen platforma uygun paket dosyalarını kullanır. Oyun güncellemeleriyle uyumluluk değişebilir.

## 🛡️ Yedekleme ve Dosya Güvenliği

Kurulum sırasında mevcut hedef dosyalar değiştirilmeden önce yedeklenir.

Yedek klasörü oyun dizininde aşağıdaki biçimde oluşturulur:

`TurkceYama-Yedek-YYYYMMDD-HHMMSS-XXXXXX`

Yedek klasöründe gerekli dosyalar ve `kurulum-kaydi.json` bulunur.

- Kurulumdan önce paket dosyalarının SHA-256 değerleri kontrol edilir.
- Kopyalanan dosyaların bütünlüğü yeniden doğrulanır.
- Tanınmayan veya çakışabilecek yükleyici dosyaları otomatik olarak değiştirilmez.
- Kurulum sırasında hata meydana gelirse değiştirilen dosyalar geri alınmaya çalışılır.

> Yedek klasörlerini silmeyin. Oyun güncellemelerinden önce dosyalarınızı ayrıca yedeklemeniz önerilir.

## ❓ Sık Sorulan Sorular

**Kurulum sırasında internet bağlantısı gerekli mi?**

Gerekli dosyaları içeren dağıtım paketi indirildikten sonra kurulum aracı çevrimdışı çalışabilir.

**Oyun dosyalarım silinir mi?**

Kurulum aracı değiştirilecek mevcut dosyaları yedekler. Yine de her dosya değişikliği belirli riskler taşıdığından önemli dosyalarınızı ayrıca yedekleyin.

**Yanlış platformu seçersem ne olur?**

Platformlara göre farklı yükleyici dosyaları kullanılır. Kurulumu tekrar gerçekleştirmeden önce doğru platformu ve oyun dizinini seçtiğinizden emin olun.

**Oyun güncellendiğinde yama çalışmaya devam eder mi?**

Uyumluluk oyunun sürümüne bağlıdır. Oyun güncellemesinden sonra yamanın yeniden düzenlenmesi gerekebilir.

**Source code ZIP dosyasını indirerek kurulum yapabilir miyim?**

Hayır, kaynak kod arşivi tam dağıtım paketi yerine geçmeyebilir. Releases bölümündeki özel ZIP dosyasını kullanın.

## 🐛 Hata Bildirimi ve Destek

Kurulum veya oyun içi Türkçe yama sorunlarını GitHub Issues üzerinden bildirebilirsiniz.

**[🐛 Hata Bildir / Destek Al](https://github.com/gggg-unit/battlefield-6-turkce-yama/issues)**

Hata bildirirken kullandığınız oyun platformunu, oyun sürümünü, karşılaştığınız hata mesajını ve sorunu yeniden oluşturma adımlarını belirtmeniz çözüm sürecini kolaylaştırır.

## ⚖️ Lisans ve Yasal Bilgilendirme

Bu depo, gggg-unit tarafından hazırlanan kurulum kodu ve projeye yapılan katkıları içerir.

Projenin kullanım, değiştirme ve yeniden dağıtım koşulları için [LICENSE](LICENSE), [NOTICE](NOTICE) ve varsa ilgili [LICENSES](LICENSES/) belgelerini inceleyin.

Battlefield ve ilgili tüm marka adları hak sahiplerine aittir. Bu proje bağımsız bir topluluk çalışmasıdır; Electronic Arts veya oyunun geliştiricileri tarafından resmî olarak desteklendiği iddia edilmez.

---

<div align="center">

**🇹🇷 Türkçe oyun deneyimi için hazırlanmıştır.**

**gggg-unit © 2026**

[GitHub](https://github.com/gggg-unit) • [Sürümler](https://github.com/gggg-unit/battlefield-6-turkce-yama/releases) • [Hata Bildir](https://github.com/gggg-unit/battlefield-6-turkce-yama/issues)

</div>
