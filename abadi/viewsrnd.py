from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404,JsonResponse
from django.urls import reverse
from . import models
from django.db.models import Sum
from urllib.parse import quote
import datetime

# Create your views here.
# RND
def gethargafg(penyusunobj):
    konversiobj = models.KonversiMaster.objects.get(
        KodePenyusun=penyusunobj.IDKodePenyusun
    )
    konversialowance = konversiobj.Kuantitas + (konversiobj.Kuantitas * 0.025)
    detailsjpembelian = models.DetailSuratJalanPembelian.objects.filter(
        KodeProduk=penyusunobj.KodeProduk
    )
    print("ini detailsjpembelian", detailsjpembelian)
    hargatotalkodeproduk = 0
    jumlahtotalkodeproduk = 0
    for m in detailsjpembelian:
        hargatotalkodeproduk += m.Harga * m.Jumlah
        jumlahtotalkodeproduk += m.Jumlah
    print("ini jumlah harga total ", hargatotalkodeproduk)
    rataratahargakodeproduk = hargatotalkodeproduk / jumlahtotalkodeproduk
    print("selesai")
    print(rataratahargakodeproduk)
    nilaifgperkodeproduk = rataratahargakodeproduk * konversialowance
    print("Harga Konversi : ", nilaifgperkodeproduk)
    return nilaifgperkodeproduk


def dashboard(request):
    dataspk = models.SPK.objects.filter(Tanggal = datetime.date.today())
    print(dataspk)
    for i in dataspk:
        detailspk = models.DetailSPK.objects.filter(NoSPK = i.id)
        i.detailspk = detailspk
    
    dataproduk = models.Produk.objects.filter(TanggalPembuatan = datetime.date.today())
    print(dataproduk)
    datasppb = models.SPPB.objects.filter(Tanggal = datetime.date.today())
    print(datasppb)
    for i in datasppb:
        detailsppb = models.DetailSPPB.objects.filter(NoSPPB=i.id)
        i.detailsppb = detailsppb
    return render(request,'rnd/dashboard.html',{'dataspk':dataspk,'dataproduk':dataproduk,'datasppb':datasppb})



def views_artikel(request):
    datakirim = []
    data = models.Artikel.objects.all()
    for item in data:
        detailartikelobj = models.Penyusun.objects.filter(KodeArtikel=item.id).filter(
            Status=1
        )
        if detailartikelobj.exists():
            datakirim.append([item, detailartikelobj[0]])
        else:
            datakirim.append([item, "Belum diset"])
    return render(request, "rnd/views_artikel.html", {"data": datakirim})


def tambahdataartikel(request):
    if request.method == "GET":
        return render(request, "rnd/tambah_artikel.html")
    if request.method == "POST":
        # print(dir(request))
        kodebaru = request.POST["kodeartikel"]
        keterangan = request.POST["keterangan"]
        data = models.Artikel.objects.filter(KodeArtikel=kodebaru).exists()
        if data:
            messages.error(request, "Kode Artikel sudah ada")
            return redirect("tambahdataartikel")
        else:
            if keterangan == '':
                keterangan = '-'
            newdataobj = models.Artikel(
                KodeArtikel=kodebaru, keterangan=keterangan
            ).save()
            messages.success(request, "Data berhasil disimpan")
            return redirect("views_artikel")


def updatedataartikel(request, id):
    data = models.Artikel.objects.get(id = id)
    if request.method == "GET":
        return render(request, "rnd/update_artikel.html",{'artikel':data})
    else:
        kodeartikel = request.POST['kodeartikel']
        keterangan = request.POST['keterangan']
        if keterangan =='':
            keterangan = '-'
        cekkodeartikel = models.Artikel.objects.filter(KodeArtikel = kodeartikel).exists()
        if cekkodeartikel:
            messages.error(request,'Kode Artikel telah terdaftar pada database')
            return redirect('update_artikel',id = id)
        else:
            data.KodeArtikel = kodeartikel
            data.keterangan = keterangan
            data.save()
            messages.success(request,'Data Berhasil diupdate')
        return redirect("views_artikel")


def deleteartikel(request, id):
    dataobj = models.Artikel.objects.get(id=id)
    dataobj.delete()
    messages.success(request,"Data Berhasil dihapus")
    return redirect("views_artikel")


def views_penyusun(request):
    print(request.GET)
    data = request.GET
    if len(request.GET) == 0:
        return render(request, "rnd/views_penyusun.html")
    else:
        kodeartikel = request.GET["kodeartikel"]
        try:
            get_id_kodeartikel = models.Artikel.objects.get(KodeArtikel=kodeartikel)
            data = models.Penyusun.objects.filter(KodeArtikel=get_id_kodeartikel.id)
            datakonversi = []
            nilaifg = 0
            if data.exists():
                for i in data:
                    konversidataobj = models.KonversiMaster.objects.get(
                        KodePenyusun=i.IDKodePenyusun
                    )
                    print(konversidataobj.Kuantitas)
                    detailsjpembelian = models.DetailSuratJalanPembelian.objects.filter(KodeProduk = i.KodeProduk)
                    hargatotalkodeproduk = 0
                    jumlahtotalkodeproduk =0
                    for j in detailsjpembelian:
                        hargatotalkodeproduk += j.Harga*j.Jumlah
                        jumlahtotalkodeproduk += j.Jumlah
                    rataratahargakodeproduk = hargatotalkodeproduk/jumlahtotalkodeproduk
                    kuantitaskonversi = konversidataobj.Kuantitas
                    kuantitasallowance = kuantitaskonversi +kuantitaskonversi*0.025
                    hargaperkotak = rataratahargakodeproduk*kuantitasallowance
                    nilaifg +=hargaperkotak

                    datakonversi.append(
                        [i, konversidataobj,kuantitasallowance,rataratahargakodeproduk,hargaperkotak]
                    )
                    
                print(data)
                print(datakonversi)
                return render(
                    request,
                    "rnd/views_penyusun.html",
                    {"data": datakonversi, "kodeartikel": get_id_kodeartikel,"nilaifg":nilaifg},
                )
            else:
                messages.error(request, "Kode Artikel Belum memiliki penyusun")
                return render(request, "rnd/views_penyusun.html",{"kodeartikel":get_id_kodeartikel})
        except models.Artikel.DoesNotExist:
            messages.error(request, "Kode Artikel Tidak ditemukan")
            return render(request, "rnd/views_penyusun.html")


def updatepenyusun(request, id):
    data = models.Penyusun.objects.get(IDKodePenyusun = id)
    if request.method == "GET":
        datakonversi = models.KonversiMaster.objects.get(KodePenyusun = data.IDKodePenyusun)
        datakonversi.allowance = datakonversi.Kuantitas + (datakonversi.Kuantitas*0.025)
        kodebahanbaku = models.Produk.objects.all()
        lokasiobj = models.Lokasi.objects.all()
        return render(request, "rnd/update_penyusun.html", {"kodestok": kodebahanbaku,"data":data,"lokasi":lokasiobj,"konversi":datakonversi})
    else :
        kodeproduk = request.POST['kodeproduk']
        lokasi = request.POST['lokasi']
        status = request.POST['status']
        kuantitas = request.POST['kuantitas']
        produkobj = models.Produk.objects.get(KodeProduk=kodeproduk)
        lokasiobj = models.Lokasi.objects.get(IDLokasi = lokasi)
        konversiobj = models.KonversiMaster.objects.get(KodePenyusun = id)
        data.KodeProduk = produkobj
        data.Lokasi = lokasiobj
        data.Status = status
        data.save()
        konversiobj.Kuantitas = kuantitas
        konversiobj.save()
        return redirect('penyusun_artikel')


def tambahdatapenyusun(request, id):
    dataartikelobj = models.Artikel.objects.get(id=id)
    if request.method == "GET":
        dataprodukobj = models.Produk.objects.all()

        return render(
            request,
            "rnd/tambah_penyusun.html",
            {"kodeartikel": dataartikelobj, "dataproduk": dataprodukobj},
        )
    else:
        kodeproduk = request.POST["kodeproduk"]
        statusproduk = request.POST["Status"]
        if statusproduk == "True":
            statusproduk = True
        else:
            statusproduk = False
        lokasi = request.POST["lokasi"]

        newprodukobj = models.Produk.objects.get(KodeProduk=kodeproduk)
        lokasiobj = models.Lokasi.objects.get(NamaLokasi=lokasi)

        datapenyusunobj= models.Penyusun.objects.filter(KodeArtikel = id).filter(Status = True).exists()
        if datapenyusunobj and statusproduk:
            messages.error(request,"Artikel telah memiliki Bahan baku utama sebelumnya")
            return redirect("tambah_data_penyusun",id=id)
        penyusunobj = models.Penyusun(
            Status=statusproduk,
            KodeArtikel=dataartikelobj,
            KodeProduk=newprodukobj,
            Lokasi=lokasiobj,
        )
        penyusunobj.save()
        kuantitas = request.POST['kuantitas']
        konversimasterobj = models.KonversiMaster(KodePenyusun=penyusunobj, Kuantitas=0).save()
        messages.success(request,"Data penyusun berhasil ditambahkan")
        
        return redirect(f"/rnd/penyusun?kodeartikel={quote(dataartikelobj.KodeArtikel)}")


# Update Delete Penyusun belum masuk
def konversi(request):
    data = request.GET
    if len(data) == 0:
        return render(request, "views_konversi.html")
    else:
        kodeartikel = request.GET["kodeartikel"]
        try:
            get_id_kodeartikel = models.Artikel.objects.get(KodeArtikel=kodeartikel)
        except models.Artikel.DoesNotExist:
            messages.error(request, "Data Artikel tidak ditemukan")
            return redirect("konversi")
        data = models.Penyusun.objects.filter(KodeArtikel=get_id_kodeartikel.id)
        if data.exists():
            listdata = []
            for i in data:
                allowance = models.KonversiMaster.objects.get(
                    KodePenyusun=i.IDKodePenyusun
                )
                listdata.append(
                    [i, allowance, allowance.Kuantitas + allowance.Kuantitas * 0.025]
                )
            return render(
                request,
                "views_konversi.html",
                {"data": listdata, "kodeartikel": kodeartikel},
            )
        else:
            return render(request, "rnd/views_konversi.html")


def konversimaster_update(request, id):
    dataobj = models.Penyusun.objects.get(IDKodePenyusun=id)
    if request.method == "GET":
        return render(request, "rnd/update_konversimaster.html", {"data": dataobj})
    else:
        konversimasterobj = models.KonversiMaster.objects.get(IDKodeKonversiMaster=id)
        print(konversimasterobj)
        konversimasterobj.Kuantitas = float(request.POST["kuantitas"])
        konversimasterobj.save()
        return redirect("konversi")


def konversimaster_delete(request, id):
    dataobj = models.KonversiMaster.objects.get(IDKodeKonversiMaster=id)
    dataobj.Kuantitas = 0
    dataobj.save()
    return redirect("konversi")

def views_sppb(request):
    data = models.SPPB.objects.all()
    for sppb in data:
        detailsppb = models.DetailSPPB.objects.filter(NoSPPB = sppb.id)
        sppb.detailsppb = detailsppb
    return render (request,'rnd/views_sppb.html',{"data":data})