# coding=utf-8
"""cdstar refactoring

Revision ID: 57204d011219
Revises: 41a8de7eec5f
Create Date: 2016-10-25 22:02:29.771101

"""
import json

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '57204d011219'
down_revision = '41a8de7eec5f'


URLMAP = {
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-0922-9845-D14C-0/49_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 688829
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-E160-65A5-8C94-0/35_282.mp3": {
        "mimetype": "audio/mpeg",
        "size": 114338
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-0BC3-BAD2-3AD2-0/72_80.mp3": {
        "mimetype": "audio/mpeg",
        "size": 27617
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-48E7-AFA8-109A-0/51_234.mp3": {
        "mimetype": "audio/mpeg",
        "size": 94615
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-3485-19DA-53C7-0/70_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 2529731
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-AD4F-F4F7-D1D2-0/51_201.mp3": {
        "mimetype": "audio/mpeg",
        "size": 139264
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-F017-65B4-5BF1-0/75_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 2740093
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-CA7F-4AD9-4D30-0/12_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1678766
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2476-7C34-DC94-0/45_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1439477
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2E17-9925-8EC9-0/17_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 47286
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-FABF-475D-5CFF-0/3_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 56359
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9B85-6443-C682-0/42_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 81880
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-F0D3-5F5E-BF03-0/72_52.mp3": {
        "mimetype": "audio/mpeg",
        "size": 57242
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-D273-2E30-A57F-0/35_273.mp3": {
        "mimetype": "audio/mpeg",
        "size": 107042
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-DE8F-DE39-DBE9-0/35_296.mp3": {
        "mimetype": "audio/mpeg",
        "size": 965632
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-8992-54C5-BF0A-0/36_166.mp3": {
        "mimetype": "audio/mpeg",
        "size": 24304
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2E17-9925-8EC9-0/17_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 728326
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-AA01-C575-5368-0/35_281.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1063936
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-77CF-4F39-D254-0/54_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 60138
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-C405-C636-A55E-0/47_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 2987541
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-F3F6-F66F-9B1E-0/1_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 50302
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7F8F-F0C0-E4CC-0/72_64.mp3": {
        "mimetype": "audio/mpeg",
        "size": 30695
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-E54E-F32F-8612-0/51_229.mp3": {
        "mimetype": "audio/mpeg",
        "size": 110168
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-3706-63C2-8EA5-0/72_98.mp3": {
        "mimetype": "audio/mpeg",
        "size": 23291
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-D8F6-D4CC-2801-0/64_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 51581
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-0D65-917F-6395-0/15_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 73915
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-D22A-2037-43B9-0/72_61.mp3": {
        "mimetype": "audio/mpeg",
        "size": 38520
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-69D7-8A1D-2369-0/72_108.mp3": {
        "mimetype": "audio/mpeg",
        "size": 43706
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6EF5-1C94-E596-0/51_225.mp3": {
        "mimetype": "audio/mpeg",
        "size": 511532
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-20F6-BE49-D7F7-0/56_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 532480
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2044-C8B2-7DBE-0/72_34.mp3": {
        "mimetype": "audio/mpeg",
        "size": 18077
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-889F-F835-01FD-0/67_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 4182938
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-E453-39B3-FDC8-0/72_25.mp3": {
        "mimetype": "audio/mpeg",
        "size": 18910
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-41D7-B3F4-A080-0/19_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 806454
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B284-E744-3BCE-0/46_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 673815
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-0EC5-7A8B-026C-0/72_158.mp3": {
        "mimetype": "audio/mpeg",
        "size": 35703
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-43D4-4263-1F01-0/4_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 52792
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5321-76EF-C623-0/72_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 76643
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-65AB-ED2B-0A34-0/33_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 4655053
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9C16-E26E-95BB-0/72_94.mp3": {
        "mimetype": "audio/mpeg",
        "size": 32678
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-643F-29BD-6A88-0/72_148.mp3": {
        "mimetype": "audio/mpeg",
        "size": 24700
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-3A3A-5DED-897B-0/72_89.mp3": {
        "mimetype": "audio/mpeg",
        "size": 50778
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7B65-1B87-E568-0/35_270.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1260544
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-C3AE-FDFE-AAC6-0/68_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 96667
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2279-47F9-8802-0/36_164.mp3": {
        "mimetype": "audio/mpeg",
        "size": 25449
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7418-0007-1C09-0/72_81.mp3": {
        "mimetype": "audio/mpeg",
        "size": 48636
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-CF1D-BC9D-57F5-0/32_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 3469152
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-272F-180B-29EC-0/72_146.mp3": {
        "mimetype": "audio/mpeg",
        "size": 27355
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5011-D4D4-6699-0/44_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 866873
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5904-B53C-DD7D-0/29_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 88514
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-A3BD-7194-7E18-0/72_113.mp3": {
        "mimetype": "audio/mpeg",
        "size": 23502
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-1F90-6D8C-32D9-0/72_134.mp3": {
        "mimetype": "audio/mpeg",
        "size": 46527
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-875F-17BE-B4A5-0/72_104.mp3": {
        "mimetype": "audio/mpeg",
        "size": 43706
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-D851-0EDF-A95A-0/72_49.mp3": {
        "mimetype": "audio/mpeg",
        "size": 44515
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-A087-34DC-4A55-0/51_211.mp3": {
        "mimetype": "audio/mpeg",
        "size": 396332
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-592B-5B36-0AD5-0/9_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 60430
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-524E-06A4-944E-0/51_215.mp3": {
        "mimetype": "audio/mpeg",
        "size": 98682
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6100-139B-1AAD-0/20_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 62792
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7592-853A-301D-0/36_163.mp3": {
        "mimetype": "audio/mpeg",
        "size": 26338
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-43FC-F459-7F28-0/34_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 73394
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-82AD-E503-DB1A-0/23_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 57073
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5916-5CA3-28EB-0/60_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 64477
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-D440-2589-5053-0/51_230.mp3": {
        "mimetype": "audio/mpeg",
        "size": 529964
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5778-98F3-A45A-0/51_199.mp3": {
        "mimetype": "audio/mpeg",
        "size": 86368
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-AEA3-B1A2-7A86-0/35_278.mp3": {
        "mimetype": "audio/mpeg",
        "size": 103874
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-3A35-3650-07D6-0/8_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 5363494
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-4D42-F53B-5312-0/35_292.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1745920
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2CD8-F16A-8A11-0/72_68.mp3": {
        "mimetype": "audio/mpeg",
        "size": 39508
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6FF4-72F0-207E-0/57_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 65621
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-F587-8D57-63AA-0/72_76.mp3": {
        "mimetype": "audio/mpeg",
        "size": 65479
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-A634-85C0-2D7B-0/30_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 51308
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-8103-A968-1BE3-0/72_35.mp3": {
        "mimetype": "audio/mpeg",
        "size": 26367
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-4559-E978-D103-0/40_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 60467
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-4A02-6FED-6382-0/65_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 51883
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-85FC-1568-D51E-0/72_15.mp3": {
        "mimetype": "audio/mpeg",
        "size": 50245
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7128-6A3F-3A49-0/37_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 59378
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-A03D-7E7F-35AA-0/2_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1795970
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-3A35-3650-07D6-0/8_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 75333
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2EA6-B600-34CA-0/72_77.mp3": {
        "mimetype": "audio/mpeg",
        "size": 37372
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-4CA6-8542-A148-0/22_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 53957
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7E04-F1F2-A42D-0/59_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 110697
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-4011-EE5E-B117-0/66_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 66891
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-D649-C0AD-D139-0/37_205.mp3": {
        "mimetype": "audio/mpeg",
        "size": 7497
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6BF9-29D4-B19D-0/72_86.mp3": {
        "mimetype": "audio/mpeg",
        "size": 5472256
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-65AB-ED2B-0A34-0/33_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 67964
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-BC2B-3054-B489-0/72_55.mp3": {
        "mimetype": "audio/mpeg",
        "size": 46293
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-237C-C3F4-20B0-0/35_236.mp3": {
        "mimetype": "audio/mpeg",
        "size": 44355
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2D12-5C7F-D4CA-0/72_110.mp3": {
        "mimetype": "audio/mpeg",
        "size": 70648
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-16B0-33CB-9534-0/76_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 55660
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-C298-E555-C6DB-0/72_75.mp3": {
        "mimetype": "audio/mpeg",
        "size": 30332
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-FDC4-0F6B-1CAC-0/61_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1622016
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-A3AC-2404-E770-0/51_202.mp3": {
        "mimetype": "audio/mpeg",
        "size": 423980
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9940-68D9-20C5-0/53_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 2166531
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-CA39-12B4-3C15-0/16_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 955502
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-0EC6-7F77-7C0F-0/72_139.mp3": {
        "mimetype": "audio/mpeg",
        "size": 18283
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-698F-E85F-B1C9-0/35_237.mp3": {
        "mimetype": "audio/mpeg",
        "size": 54723
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-CA39-12B4-3C15-0/16_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 65563
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-FD8D-1F10-64ED-0/51_219.mp3": {
        "mimetype": "audio/mpeg",
        "size": 557612
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-1229-A05B-FDE9-0/72_171.mp3": {
        "mimetype": "audio/mpeg",
        "size": 47126
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7B89-0EA2-EB8A-0/26_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 91822
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B413-8B91-8171-0/51_231.mp3": {
        "mimetype": "audio/mpeg",
        "size": 447020
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-E4EE-BA1B-986F-0/72_156.mp3": {
        "mimetype": "audio/mpeg",
        "size": 35443
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7B89-0EA2-EB8A-0/26_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1782594
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-33C3-9410-9AB6-0/35_230.mp3": {
        "mimetype": "audio/mpeg",
        "size": 134499
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-C39E-63BB-8877-0/72_12.mp3": {
        "mimetype": "audio/mpeg",
        "size": 92184
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B86B-35E9-90AF-0/31_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 56029
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-289F-0571-2279-0/35_286.mp3": {
        "mimetype": "audio/mpeg",
        "size": 762880
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-3C92-F478-F092-0/72_135.mp3": {
        "mimetype": "audio/mpeg",
        "size": 48040
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-FA0D-34A4-432A-0/18_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 2455543
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-DC74-4D84-DC5E-0/51_222.mp3": {
        "mimetype": "audio/mpeg",
        "size": 97436
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-1B18-AD89-7D6E-0/51_226.mp3": {
        "mimetype": "audio/mpeg",
        "size": 571436
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6B7E-67CE-EBC0-0/72_67.mp3": {
        "mimetype": "audio/mpeg",
        "size": 42901
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6BEC-91F4-D73F-0/72_50.mp3": {
        "mimetype": "audio/mpeg",
        "size": 25219
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-09B3-8B85-1993-0/35_263.mp3": {
        "mimetype": "audio/mpeg",
        "size": 121059
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5C72-890E-8130-0/35_293.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1604608
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-60EF-24E9-B342-0/72_118.mp3": {
        "mimetype": "audio/mpeg",
        "size": 44098
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9106-04DE-CE9F-0/51_217.mp3": {
        "mimetype": "audio/mpeg",
        "size": 90024
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5321-76EF-C623-0/72_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1012539
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-0044-6BA6-61AF-0/35_231.mp3": {
        "mimetype": "audio/mpeg",
        "size": 115107
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-069F-29D5-FBB8-0/72_149.mp3": {
        "mimetype": "audio/mpeg",
        "size": 34869
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5011-D4D4-6699-0/44_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 59198
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7E04-F1F2-A42D-0/59_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 2506752
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-E33C-4B0C-7492-0/51_204.mp3": {
        "mimetype": "audio/mpeg",
        "size": 111525
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-A242-C970-D31B-0/35_279.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1254400
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-EF6D-C764-3FE7-0/51_216.mp3": {
        "mimetype": "audio/mpeg",
        "size": 95554
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9D05-735A-EB57-0/35_304.mp3": {
        "mimetype": "audio/mpeg",
        "size": 98161
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5D7E-EAB1-9B70-0/72_109.mp3": {
        "mimetype": "audio/mpeg",
        "size": 123267
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-8A06-FA1D-7900-0/72_63.mp3": {
        "mimetype": "audio/mpeg",
        "size": 48040
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7F6F-642B-9FE4-0/35_280.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1125376
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-74FC-4647-963C-0/72_162.mp3": {
        "mimetype": "audio/mpeg",
        "size": 30279
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7FF1-D1A4-9B1B-0/72_40.mp3": {
        "mimetype": "audio/mpeg",
        "size": 26630
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-D472-E61A-36B3-0/72_36.mp3": {
        "mimetype": "audio/mpeg",
        "size": 22456
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-A791-7238-74C1-0/72_168.mp3": {
        "mimetype": "audio/mpeg",
        "size": 25531
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-CADB-7E6C-EEA4-0/72_37.mp3": {
        "mimetype": "audio/mpeg",
        "size": 25012
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-84D2-7730-F42A-0/72_23.mp3": {
        "mimetype": "audio/mpeg",
        "size": 50828
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-FA0D-34A4-432A-0/18_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 54715
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-FE27-4ED1-3332-0/13_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 68430
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-669A-AE94-D238-0/35_291.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1205248
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9800-7D02-6B17-0/72_96.mp3": {
        "mimetype": "audio/mpeg",
        "size": 21257
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B455-7D85-D7DF-0/72_103.mp3": {
        "mimetype": "audio/mpeg",
        "size": 60059
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-68C6-B358-581F-0/35_295.mp3": {
        "mimetype": "audio/mpeg",
        "size": 136316
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6C41-B2A8-6D15-0/51_207.mp3": {
        "mimetype": "audio/mpeg",
        "size": 108501
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-72D7-1555-6287-0/35_300.mp3": {
        "mimetype": "audio/mpeg",
        "size": 97922
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-DF10-DC71-8617-0/51_235.mp3": {
        "mimetype": "audio/mpeg",
        "size": 428588
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6069-7C12-765E-0/11_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 52165
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2357-7D42-BDF0-0/72_73.mp3": {
        "mimetype": "audio/mpeg",
        "size": 41649
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2620-AC67-64E7-0/35_100.mp3": {
        "mimetype": "audio/mpeg",
        "size": 145635
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-8043-6EAE-7477-0/72_120.mp3": {
        "mimetype": "audio/mpeg",
        "size": 36643
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B62A-6C0F-AAD1-0/5_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 81859
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-C405-C636-A55E-0/47_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 89990
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-657C-15B3-C77E-0/36_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 358015
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7756-600B-3E45-0/7_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 89855
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-42F3-29C8-F0CF-0/72_167.mp3": {
        "mimetype": "audio/mpeg",
        "size": 33248
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-FDC4-0F6B-1CAC-0/61_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 65673
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5738-22E4-18BC-0/48_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 73699
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-F04A-1525-E202-0/72_102.mp3": {
        "mimetype": "audio/mpeg",
        "size": 26000
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9BDD-3859-93E4-0/51_224.mp3": {
        "mimetype": "audio/mpeg",
        "size": 488492
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-DAB3-B74D-088D-0/72_85.mp3": {
        "mimetype": "audio/mpeg",
        "size": 38568
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-3220-83D9-1D4C-0/28_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 76676
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-77F2-9A04-6BA9-0/72_165.mp3": {
        "mimetype": "audio/mpeg",
        "size": 20841
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-1DC6-28E5-C84A-0/6_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 47658
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6969-3C9C-2AC9-0/35_294.mp3": {
        "mimetype": "audio/mpeg",
        "size": 85249
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7756-600B-3E45-0/7_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 4053158
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-14A2-9276-DD1A-0/51_210.mp3": {
        "mimetype": "audio/mpeg",
        "size": 83861
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-47E4-6ED3-093B-0/36_165.mp3": {
        "mimetype": "audio/mpeg",
        "size": 25922
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B38A-3988-8D99-0/51_206.mp3": {
        "mimetype": "audio/mpeg",
        "size": 84173
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-CB14-3BD6-42B5-0/51_209.mp3": {
        "mimetype": "audio/mpeg",
        "size": 94826
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-43D4-4263-1F01-0/4_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1336457
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-1DC6-28E5-C84A-0/6_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 90112
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B214-2D4B-7ABF-0/24_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 46303
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5C2C-EC2E-3D81-0/37_248.mp3": {
        "mimetype": "audio/mpeg",
        "size": 6601
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9DBA-CA43-78F1-0/72_106.mp3": {
        "mimetype": "audio/mpeg",
        "size": 32573
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-F703-C5B6-27B9-0/72_71.mp3": {
        "mimetype": "audio/mpeg",
        "size": 37372
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2521-2D32-F148-0/72_59.mp3": {
        "mimetype": "audio/mpeg",
        "size": 40035
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-84F8-5EAE-67DE-0/39_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 76600
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9940-68D9-20C5-0/53_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 86450
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6016-9696-A1FE-0/51_233.mp3": {
        "mimetype": "audio/mpeg",
        "size": 94719
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-01BC-C33E-0726-0/72_95.mp3": {
        "mimetype": "audio/mpeg",
        "size": 27255
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2D77-4448-187F-0/35_274.mp3": {
        "mimetype": "audio/mpeg",
        "size": 120386
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-21F5-B649-704C-0/72_69.mp3": {
        "mimetype": "audio/mpeg",
        "size": 93281
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-C116-1703-A749-0/51_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 88990
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6C86-FBE4-309D-0/72_160.mp3": {
        "mimetype": "audio/mpeg",
        "size": 106085
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-3485-19DA-53C7-0/70_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 57141
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-BC4A-1547-7599-0/72_29.mp3": {
        "mimetype": "audio/mpeg",
        "size": 33252
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-182A-829B-1381-0/52_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 58753
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-CA7F-4AD9-4D30-0/12_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 84895
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-74A6-C065-9A75-0/51_223.mp3": {
        "mimetype": "audio/mpeg",
        "size": 502316
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5FA9-1AE2-0BB7-0/35_299.mp3": {
        "mimetype": "audio/mpeg",
        "size": 109826
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B069-A8E4-3D26-0/72_60.mp3": {
        "mimetype": "audio/mpeg",
        "size": 20893
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-889F-F835-01FD-0/67_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 63398
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-FCF3-869A-7E01-0/69_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 71956
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-41D7-B3F4-A080-0/19_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 71051
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-8D7B-BDCF-3D0D-0/62_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 72985
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B8FF-644C-7050-0/72_27.mp3": {
        "mimetype": "audio/mpeg",
        "size": 16095
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-10A8-8D9C-BBB9-0/72_46.mp3": {
        "mimetype": "audio/mpeg",
        "size": 42173
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5916-5CA3-28EB-0/60_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 290305
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-4CA6-8542-A148-0/22_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1347648
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-3C99-A884-4D7D-0/51_220.mp3": {
        "mimetype": "audio/mpeg",
        "size": 121027
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2D91-916D-CC5D-0/25_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 73233
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-C7B8-E297-0F95-0/72_153.mp3": {
        "mimetype": "audio/mpeg",
        "size": 24802
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9175-318E-0D12-0/72_66.mp3": {
        "mimetype": "audio/mpeg",
        "size": 28740
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B6DD-0D82-8C5F-0/27_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 91012
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9B85-6443-C682-0/42_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 7322677
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7FB5-1F8B-7762-0/72_121.mp3": {
        "mimetype": "audio/mpeg",
        "size": 25431
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2B98-94B7-A19D-0/35_303.mp3": {
        "mimetype": "audio/mpeg",
        "size": 134114
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B284-E744-3BCE-0/46_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 68303
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-D4EA-7356-0377-0/72_20.mp3": {
        "mimetype": "audio/mpeg",
        "size": 16851
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-0D65-917F-6395-0/15_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 2269962
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9DBC-4C82-7FB7-0/35_265.mp3": {
        "mimetype": "audio/mpeg",
        "size": 161187
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-82AD-E503-DB1A-0/23_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 262
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-3CBC-B629-157B-0/35_290.mp3": {
        "mimetype": "audio/mpeg",
        "size": 125569
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-42CC-D08E-3915-0/72_57.mp3": {
        "mimetype": "audio/mpeg",
        "size": 54424
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-D49C-6B98-54E5-0/72_65.mp3": {
        "mimetype": "audio/mpeg",
        "size": 30489
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-F745-4383-D866-0/72_170.mp3": {
        "mimetype": "audio/mpeg",
        "size": 93433
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-65E7-6B27-CE91-0/35_262.mp3": {
        "mimetype": "audio/mpeg",
        "size": 120051
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-F905-3ADD-AA91-0/72_105.mp3": {
        "mimetype": "audio/mpeg",
        "size": 69498
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-4559-E978-D103-0/40_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 990244
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2BEF-BCCD-AEF5-0/14_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1893733
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-8008-C65A-ED25-0/74_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 66921
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2BEF-BCCD-AEF5-0/14_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 53700
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-657C-15B3-C77E-0/36_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 60434
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-837B-2863-5A13-0/37_207.mp3": {
        "mimetype": "audio/mpeg",
        "size": 13001
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-20F6-BE49-D7F7-0/56_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 73673
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2252-D86E-C0EB-0/35_264.mp3": {
        "mimetype": "audio/mpeg",
        "size": 103203
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-CA08-195F-58EA-0/35_288.mp3": {
        "mimetype": "audio/mpeg",
        "size": 132578
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5738-22E4-18BC-0/48_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 607712
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-4A62-531D-4141-0/72_136.mp3": {
        "mimetype": "audio/mpeg",
        "size": 22875
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-931C-5EF7-76FF-0/72_107.mp3": {
        "mimetype": "audio/mpeg",
        "size": 70648
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5831-BDC8-5BC1-0/72_144.mp3": {
        "mimetype": "audio/mpeg",
        "size": 50878
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-D8F6-D4CC-2801-0/64_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 568503
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7C8D-14BA-B2AC-0/72_157.mp3": {
        "mimetype": "audio/mpeg",
        "size": 36277
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7BA9-1923-57AC-0/55_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 62892
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-066E-6B26-55E6-0/72_70.mp3": {
        "mimetype": "audio/mpeg",
        "size": 43317
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2D91-916D-CC5D-0/25_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 495314
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-A634-85C0-2D7B-0/30_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 2754384
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-F017-65B4-5BF1-0/75_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 66334
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-43FC-F459-7F28-0/34_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 3881829
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-F355-EBC4-708C-0/71_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 57903
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-AA07-3120-F192-0/72_99.mp3": {
        "mimetype": "audio/mpeg",
        "size": 40863
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6069-7C12-765E-0/11_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 560516
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-D4A7-28A1-6B52-0/72_33.mp3": {
        "mimetype": "audio/mpeg",
        "size": 12627
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-A5EA-BB44-8AED-0/72_115.mp3": {
        "mimetype": "audio/mpeg",
        "size": 21985
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6EF5-D1B7-8C4C-0/72_137.mp3": {
        "mimetype": "audio/mpeg",
        "size": 60057
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-182A-829B-1381-0/52_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1900669
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-1D48-AAF9-7426-0/35_287.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1358848
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6442-67EF-C9AD-0/58_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 76900
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-BCE5-E301-C0FA-0/35_272.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1297408
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-DD53-3548-FE55-0/10_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 65351
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-AC40-B4D9-633B-0/50_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 88990
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5EE1-C0F6-EAF1-0/72_51.mp3": {
        "mimetype": "audio/mpeg",
        "size": 57028
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-33B8-935A-A031-0/72_125.mp3": {
        "mimetype": "audio/mpeg",
        "size": 14010
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9F51-6A5A-8F1C-0/51_205.mp3": {
        "mimetype": "audio/mpeg",
        "size": 24576
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-AC3D-0993-5C74-0/35_261.mp3": {
        "mimetype": "audio/mpeg",
        "size": 113954
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-E98D-6BD7-8F78-0/35_301.mp3": {
        "mimetype": "audio/mpeg",
        "size": 82748
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7BA9-1923-57AC-0/55_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 2023424
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-A03D-7E7F-35AA-0/2_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 71503
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9F5A-DB25-7293-0/51_228.mp3": {
        "mimetype": "audio/mpeg",
        "size": 502316
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-8008-C65A-ED25-0/74_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 3359380
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-29B5-D160-EE25-0/37_208.mp3": {
        "mimetype": "audio/mpeg",
        "size": 8411
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-061D-A4C2-4443-0/35_275.mp3": {
        "mimetype": "audio/mpeg",
        "size": 108386
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-1CB0-06AF-55DD-0/41_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 114600
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-1CB0-06AF-55DD-0/41_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 876544
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5AAB-6349-E0BD-0/51_203.mp3": {
        "mimetype": "audio/mpeg",
        "size": 100356
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9C03-1E6A-6234-0/72_16.mp3": {
        "mimetype": "audio/mpeg",
        "size": 22093
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-0922-9845-D14C-0/49_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 61499
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-CE2E-1399-D1CC-0/72_88.mp3": {
        "mimetype": "audio/mpeg",
        "size": 19718
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-FCF3-869A-7E01-0/69_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 3507804
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7CA6-2A6E-D997-0/35_258.mp3": {
        "mimetype": "audio/mpeg",
        "size": 319010
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-FA85-8BBB-2538-0/35_298.mp3": {
        "mimetype": "audio/mpeg",
        "size": 2176000
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-FC11-9C1E-D5CD-0/72_129.mp3": {
        "mimetype": "audio/mpeg",
        "size": 78835
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-4011-EE5E-B117-0/66_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1079520
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-1ED0-FCD0-EBB0-0/35_297.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1684480
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-3311-EE23-CF86-0/63_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 60698
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-94D8-9919-7C8F-0/51_214.mp3": {
        "mimetype": "audio/mpeg",
        "size": 100568
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-1E70-0DAF-817A-0/72_84.mp3": {
        "mimetype": "audio/mpeg",
        "size": 26817
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7B8D-AE61-115A-0/35_284.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1014784
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-CF1D-BC9D-57F5-0/32_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 85220
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-1A77-9CA0-9350-0/35_276.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1512448
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-FCCE-7085-4EF2-0/72_169.mp3": {
        "mimetype": "audio/mpeg",
        "size": 48425
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-373B-4AD9-E7AF-0/51_200.mp3": {
        "mimetype": "audio/mpeg",
        "size": 451628
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-3245-E2F6-EB02-0/72_145.mp3": {
        "mimetype": "audio/mpeg",
        "size": 55734
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-70E3-9E18-ADBB-0/35_271.mp3": {
        "mimetype": "audio/mpeg",
        "size": 103298
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7E8E-5EEA-1F95-0/51_208.mp3": {
        "mimetype": "audio/mpeg",
        "size": 456236
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-32C4-352B-4F66-0/72_56.mp3": {
        "mimetype": "audio/mpeg",
        "size": 46318
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2564-62A6-E107-0/43_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 65461
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-4A1C-4F75-12C8-0/72_79.mp3": {
        "mimetype": "audio/mpeg",
        "size": 63706
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-1B59-0103-25F3-0/72_22.mp3": {
        "mimetype": "audio/mpeg",
        "size": 50879
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-A06C-29B8-A0F3-0/50_246.mp3": {
        "mimetype": "audio/mpeg",
        "size": 695852
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-DB71-C3D3-6C42-0/72_54.mp3": {
        "mimetype": "audio/mpeg",
        "size": 70648
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-E90B-E0A5-D843-0/73_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 58316
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-3823-5313-D772-0/51_212.mp3": {
        "mimetype": "audio/mpeg",
        "size": 104322
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9F53-34DD-455D-0/72_38.mp3": {
        "mimetype": "audio/mpeg",
        "size": 19281
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-40E1-BA62-E02D-0/37_206.mp3": {
        "mimetype": "audio/mpeg",
        "size": 7863
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-1916-0195-8DC7-0/35_305.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1211392
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6A4D-5E19-1000-0/72_138.mp3": {
        "mimetype": "audio/mpeg",
        "size": 22144
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5BF9-C320-B649-0/72_13.mp3": {
        "mimetype": "audio/mpeg",
        "size": 74456
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-D5B5-C23F-4D43-0/72_41.mp3": {
        "mimetype": "audio/mpeg",
        "size": 26886
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-FB07-2BA6-E854-0/72_28.mp3": {
        "mimetype": "audio/mpeg",
        "size": 18807
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-5CC0-9AB9-F22A-0/72_114.mp3": {
        "mimetype": "audio/mpeg",
        "size": 27969
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7128-6A3F-3A49-0/37_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 337535
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-910A-B37C-4A4C-0/72_72.mp3": {
        "mimetype": "audio/mpeg",
        "size": 27617
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-421A-D81B-1AB9-0/72_14.mp3": {
        "mimetype": "audio/mpeg",
        "size": 59949
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-46B5-FDB0-FDA2-0/72_78.mp3": {
        "mimetype": "audio/mpeg",
        "size": 37009
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B3DF-91C6-BBDD-0/72_112.mp3": {
        "mimetype": "audio/mpeg",
        "size": 24963
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-8C88-97A2-1DD4-0/35_283.mp3": {
        "mimetype": "audio/mpeg",
        "size": 105794
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-964D-5819-4FE9-0/72_147.mp3": {
        "mimetype": "audio/mpeg",
        "size": 49155
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9DAD-1B44-F9B2-0/51_218.mp3": {
        "mimetype": "audio/mpeg",
        "size": 112051
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2E5F-CB60-0FC0-0/51_221.mp3": {
        "mimetype": "audio/mpeg",
        "size": 97020
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-8D7B-BDCF-3D0D-0/62_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 5270498
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-8B72-8755-807F-0/35_285.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1180672
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-FE27-4ED1-3332-0/13_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 505330
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-D51D-F22B-6B7E-0/51_227.mp3": {
        "mimetype": "audio/mpeg",
        "size": 400940
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-AC40-B4D9-633B-0/50_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 3139951
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7B07-3251-9A05-0/72_47.mp3": {
        "mimetype": "audio/mpeg",
        "size": 40766
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-982A-72C2-648A-0/35_289.mp3": {
        "mimetype": "audio/mpeg",
        "size": 108578
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-6D47-71C7-3F55-0/51_232.mp3": {
        "mimetype": "audio/mpeg",
        "size": 516140
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2476-7C34-DC94-0/45_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 65282
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-0CE7-D655-B331-0/41_38.mp3": {
        "mimetype": "audio/mpeg",
        "size": 432000
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-8FCC-3888-676A-0/72_116.mp3": {
        "mimetype": "audio/mpeg",
        "size": 44098
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B8D1-30F8-7D83-0/72_26.mp3": {
        "mimetype": "audio/mpeg",
        "size": 18336
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B0B9-790D-6A4D-0/38_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 52540
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-2447-D626-3F47-0/72_150.mp3": {
        "mimetype": "audio/mpeg",
        "size": 20970
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-9A06-0FA3-3115-0/72_161.mp3": {
        "mimetype": "audio/mpeg",
        "size": 44776
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-B959-1134-68BD-0/72_166.mp3": {
        "mimetype": "audio/mpeg",
        "size": 28769
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7D6D-0953-8485-0/35_gt.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1602906
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-843F-87AB-CEED-0/35_277.mp3": {
        "mimetype": "audio/mpeg",
        "size": 1266688
    },
    "https://cdstar.shh.mpg.de/bitstreams/EAEA0-7D6D-0953-8485-0/35_gt.pdf": {
        "mimetype": "application/pdf",
        "size": 57313
    }
}


def update_url(table, pk, d):
    op.execute(
        sa.text('UPDATE %s SET jsondata = :jsondata WHERE pk = :pk' % table)
            .bindparams(jsondata=json.dumps(d), pk=pk))


def upgrade():
    conn = op.get_bind()
    for table in ['sentence_files', 'contribution_files']:
        for pk, jsondata in conn.execute(
                "select pk, jsondata from %s" % table).fetchall():
            url = json.loads(jsondata)['url']
            d = URLMAP[url]
            comps = url.split('/')
            d.update(objid=comps[-2], original=comps[-1])
            update_url(table, pk, d)


def downgrade():
    pass
