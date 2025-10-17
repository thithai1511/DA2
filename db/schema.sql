-- File: DIemdanh.sql (doi het ten bang/cot sang tieng Viet khong dau)
-- He thong diem danh bang khuon mat, tuong thich MySQL/MariaDB
-- Collation toan cuc: utf8mb4_general_ci

CREATE DATABASE IF NOT EXISTS diem_danh
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;
USE diem_danh;

-- =========================
-- 1) SINH_VIEN
-- =========================
CREATE TABLE IF NOT EXISTS sinh_vien (
    mssv            VARCHAR(10)  PRIMARY KEY,
    ho_ten          VARCHAR(100) NOT NULL,
    lop             VARCHAR(20),
    email           VARCHAR(100),
    so_dien_thoai   VARCHAR(15),
    ngay_sinh       DATE,
    gioi_tinh       ENUM('Nam','Nu','Khac') DEFAULT 'Nam',
    khoa_hoc        VARCHAR(10),
    khoa            VARCHAR(100),
    nganh_hoc       VARCHAR(100),
    trang_thai      ENUM('Dang hoc','Da nghi','Bao luu') DEFAULT 'Dang hoc',
    tao_luc      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cap_nhat_luc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE INDEX idx_sv_lop   ON sinh_vien(lop);
CREATE INDEX idx_sv_email ON sinh_vien(email);

-- =========================
-- 2) GIANG_VIEN
-- =========================
CREATE TABLE IF NOT EXISTS giang_vien (
    ma_giang_vien   VARCHAR(10)  PRIMARY KEY,
    ho_ten          VARCHAR(100) NOT NULL,
    email           VARCHAR(100) UNIQUE,
    so_dien_thoai   VARCHAR(15),
    mat_khau        VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE INDEX idx_gv_email ON giang_vien(email);

-- =========================
-- 3) LOP_HOC
-- =========================
CREATE TABLE IF NOT EXISTS lop_hoc (
    ma_lop              VARCHAR(10) PRIMARY KEY,
    ten_mon_hoc         VARCHAR(100) NOT NULL,
    phong_hoc           VARCHAR(20),
    thoi_gian_bat_dau   DATETIME,
    thoi_gian_ket_thuc  DATETIME,
    ma_giang_vien       VARCHAR(10),
    CONSTRAINT fk_lh_gv FOREIGN KEY (ma_giang_vien)
        REFERENCES giang_vien(ma_giang_vien)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_thoi_gian_lop CHECK (thoi_gian_ket_thuc > thoi_gian_bat_dau)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE INDEX idx_lh_gv ON lop_hoc(ma_giang_vien);

-- =========================
-- 4) DANG_KY_LOP
-- =========================
CREATE TABLE IF NOT EXISTS dang_ky_lop (
    ma_dang_ky      INT AUTO_INCREMENT PRIMARY KEY,
    mssv            VARCHAR(10) NOT NULL,
    ma_lop          VARCHAR(10) NOT NULL,
    ngay_dang_ky    DATETIME DEFAULT CURRENT_TIMESTAMP,
    trang_thai      ENUM('Da dang ky','Da huy') DEFAULT 'Da dang ky',
    UNIQUE KEY uk_dk (mssv, ma_lop),
    CONSTRAINT fk_dk_sv  FOREIGN KEY (mssv)  REFERENCES sinh_vien(mssv) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_dk_lop FOREIGN KEY (ma_lop) REFERENCES lop_hoc(ma_lop) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE INDEX idx_dk_mssv  ON dang_ky_lop(mssv);
CREATE INDEX idx_dk_malop ON dang_ky_lop(ma_lop);

-- =========================
-- 5) ANH_KHUON_MAT (mau anh da cat tu FaceDetect.py)
-- =========================
CREATE TABLE IF NOT EXISTS anh_khuon_mat (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    mssv            VARCHAR(10) NOT NULL,
    duong_dan_tep   VARCHAR(255) NOT NULL, -- vi du: dataset/22520123/22520123_1.jpg
    thoi_diem_chup  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_akm_mssv (mssv),
    CONSTRAINT fk_akm_sv FOREIGN KEY (mssv)
        REFERENCES sinh_vien(mssv)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =========================
-- 6) CONG_VIEC_HUAN_LUYEN (train encodings)
-- =========================
CREATE TABLE IF NOT EXISTS cong_viec_huan_luyen (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    trang_thai          ENUM('QUEUED','RUNNING','SUCCESS','FAILED') NOT NULL DEFAULT 'QUEUED',
    bat_dau_luc         TIMESTAMP NULL,
    ket_thuc_luc        TIMESTAMP NULL,
    danh_sach_mssv      JSON NULL,  -- danh sach MSSV moi them vao encodings
    phien_ban_mo_hinh   VARCHAR(32) NULL,
    ghi_chu             TEXT NULL,
    PRIMARY KEY (id),
    INDEX idx_cvhl_trang_thai (trang_thai)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =========================
-- 7) DIEM_DANH (nhan dien khuon mat)
-- =========================
CREATE TABLE IF NOT EXISTS diem_danh (
    ma_diem_danh        INT AUTO_INCREMENT PRIMARY KEY,
    mssv                VARCHAR(10) NOT NULL,
    ma_lop              VARCHAR(10) NOT NULL,
    thoi_gian_diem_danh DATETIME NOT NULL,
    ma_thiet_bi         VARCHAR(64) NOT NULL DEFAULT 'pi5-cam-01',
    do_tin_cay          TINYINT UNSIGNED NULL, -- 0-100 neu co
    duong_dan_anh       VARCHAR(255) NULL,     -- duong dan anh frame neu co luu
    phien_ban_mo_hinh   VARCHAR(32)  NULL,
    nguon_nhan_dien     ENUM('face') DEFAULT 'face',
    trang_thai          ENUM('Hop le','Gian lan','Vang mat') DEFAULT 'Hop le',
    CONSTRAINT fk_dd_sv   FOREIGN KEY (mssv)   REFERENCES sinh_vien(mssv) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_dd_lop  FOREIGN KEY (ma_lop) REFERENCES lop_hoc(ma_lop) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE INDEX idx_dd_mssv     ON diem_danh(mssv);
CREATE INDEX idx_dd_malop    ON diem_danh(ma_lop);
CREATE INDEX idx_dd_time     ON diem_danh(thoi_gian_diem_danh);

-- =========================
-- 8) CANH_BAO_GIAN_LAN
-- =========================
CREATE TABLE IF NOT EXISTS canh_bao_gian_lan (
    ma_canh_bao         INT AUTO_INCREMENT PRIMARY KEY,
    ma_diem_danh        INT NOT NULL,
    loai_canh_bao       ENUM('Diem danh trung','Sinh vien khong co trong lop') NOT NULL,
    mo_ta               TEXT,
    thoi_gian_phat_hien DATETIME DEFAULT CURRENT_TIMESTAMP,
    trang_thai          ENUM('Chua xu ly','Da xac minh','Da xu ly') DEFAULT 'Chua xu ly',
    ma_giang_vien_xu_ly VARCHAR(10),
    CONSTRAINT fk_cb_dd  FOREIGN KEY (ma_diem_danh)        REFERENCES diem_danh(ma_diem_danh) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_cb_gv  FOREIGN KEY (ma_giang_vien_xu_ly) REFERENCES giang_vien(ma_giang_vien) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE INDEX idx_cb_trang_thai ON canh_bao_gian_lan(trang_thai);

-- =========================
-- 9) LICH_SU_CANH_BAO
-- =========================
CREATE TABLE IF NOT EXISTS lich_su_canh_bao (
    ma_lich_su              INT AUTO_INCREMENT PRIMARY KEY,
    ma_canh_bao             INT NOT NULL,
    hanh_dong               ENUM('Tao canh bao','Xac minh','Xu ly','Bo qua') NOT NULL,
    mo_ta                   TEXT,
    thoi_gian               DATETIME DEFAULT CURRENT_TIMESTAMP,
    ma_giang_vien_thuc_hien VARCHAR(10) NOT NULL,
    CONSTRAINT fk_lscb_cb FOREIGN KEY (ma_canh_bao)             REFERENCES canh_bao_gian_lan(ma_canh_bao) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_lscb_gv FOREIGN KEY (ma_giang_vien_thuc_hien)  REFERENCES giang_vien(ma_giang_vien)     ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE INDEX idx_lscb_time ON lich_su_canh_bao(thoi_gian);

-- =========================
-- 10) LICH_SU_DIEM_DANH (snapshot thong tin)
-- =========================
CREATE TABLE IF NOT EXISTS lich_su_diem_danh (
    ma_lich_su              INT AUTO_INCREMENT PRIMARY KEY,
    mssv                    VARCHAR(10) NOT NULL,
    ho_ten                  VARCHAR(100) NOT NULL,
    lop                     VARCHAR(20),
    so_dien_thoai           VARCHAR(15),
    ngay_sinh               DATE,
    gioi_tinh               ENUM('Nam','Nu','Khac'),
    thoi_gian_diem_danh     DATETIME NOT NULL,
    ma_lop                  VARCHAR(10) NOT NULL,
    trang_thai_diem_danh    ENUM('Hop le','Gian lan','Vang mat') DEFAULT 'Hop le',
    ma_thiet_bi             VARCHAR(64),
    do_tin_cay              TINYINT UNSIGNED,
    duong_dan_anh           VARCHAR(255),
    phien_ban_mo_hinh       VARCHAR(32),
    CONSTRAINT fk_lsd_sv   FOREIGN KEY (mssv)   REFERENCES sinh_vien(mssv) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_lsd_lop  FOREIGN KEY (ma_lop) REFERENCES lop_hoc(ma_lop) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE INDEX idx_lsd_mssv     ON lich_su_diem_danh(mssv);
CREATE INDEX idx_lsd_thoigian ON lich_su_diem_danh(thoi_gian_diem_danh);
CREATE INDEX idx_lsd_malop    ON lich_su_diem_danh(ma_lop);

-- =========================
-- 11) TRIGGER kiem tra gian lan
-- =========================
DELIMITER //
CREATE TRIGGER trg_kiem_tra_gian_lan
AFTER INSERT ON diem_danh
FOR EACH ROW
BEGIN
    DECLARE sinh_vien_trong_lop INT DEFAULT 0;
    DECLARE diem_danh_trung INT DEFAULT 0;

    SELECT COUNT(*) INTO sinh_vien_trong_lop
    FROM dang_ky_lop
    WHERE mssv = NEW.mssv AND ma_lop = NEW.ma_lop AND trang_thai = 'Da dang ky';

    SELECT COUNT(*) INTO diem_danh_trung
    FROM diem_danh
    WHERE mssv = NEW.mssv
      AND ma_lop = NEW.ma_lop
      AND ABS(TIMESTAMPDIFF(MINUTE, thoi_gian_diem_danh, NEW.thoi_gian_diem_danh)) <= 5
      AND ma_diem_danh != NEW.ma_diem_danh;

    IF sinh_vien_trong_lop = 0 OR diem_danh_trung > 0 THEN
        UPDATE diem_danh
        SET trang_thai = 'Gian lan'
        WHERE ma_diem_danh = NEW.ma_diem_danh;

        IF sinh_vien_trong_lop = 0 THEN
            INSERT INTO canh_bao_gian_lan (ma_diem_danh, loai_canh_bao, mo_ta)
            VALUES (NEW.ma_diem_danh, 'Sinh vien khong co trong lop',
                    CONCAT('SV ', NEW.mssv, ' diem danh lop ', NEW.ma_lop, ' nhung khong dang ky'));
        ELSE
            INSERT INTO canh_bao_gian_lan (ma_diem_danh, loai_canh_bao, mo_ta)
            VALUES (NEW.ma_diem_danh, 'Diem danh trung',
                    CONCAT('SV ', NEW.mssv, ' diem danh trung trong khoang thoi gian ngan'));
        END IF;
    END IF;
END//
DELIMITER ;

-- =========================
-- 12) TRIGGER dong bo lich su diem danh
-- =========================
DELIMITER //
CREATE TRIGGER trg_dong_bo_lich_su
AFTER INSERT ON diem_danh
FOR EACH ROW
BEGIN
    INSERT INTO lich_su_diem_danh (
        mssv, ho_ten, lop, so_dien_thoai, ngay_sinh, gioi_tinh,
        thoi_gian_diem_danh, ma_lop, trang_thai_diem_danh,
        ma_thiet_bi, do_tin_cay, duong_dan_anh, phien_ban_mo_hinh
    )
    SELECT
        s.mssv, s.ho_ten, s.lop, s.so_dien_thoai, s.ngay_sinh, s.gioi_tinh,
        NEW.thoi_gian_diem_danh, NEW.ma_lop, NEW.trang_thai,
        NEW.ma_thiet_bi, NEW.do_tin_cay, NEW.duong_dan_anh, NEW.phien_ban_mo_hinh
    FROM sinh_vien s
    WHERE s.mssv = NEW.mssv;
END//
DELIMITER ;

-- =========================
-- 13) VIEW: diem danh moi nhat trong ngay theo mssv + lop
-- =========================
DROP VIEW IF EXISTS v_diem_danh_moi_nhat_trong_ngay;
CREATE VIEW v_diem_danh_moi_nhat_trong_ngay AS
SELECT d.*
FROM diem_danh d
JOIN (
    SELECT mssv, ma_lop, MAX(thoi_gian_diem_danh) AS lan_cuoi
    FROM diem_danh
    WHERE DATE(thoi_gian_diem_danh) = CURRENT_DATE()
    GROUP BY mssv, ma_lop
) x ON x.mssv = d.mssv AND x.ma_lop = d.ma_lop AND x.lan_cuoi = d.thoi_gian_diem_danh;
