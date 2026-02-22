-- 1. Tabel User (Admin)
CREATE TABLE IF NOT EXISTS `user` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(150) NOT NULL UNIQUE,
  `password_hash` VARCHAR(256) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Tabel Item (Master Data Barang)
CREATE TABLE IF NOT EXISTS `item` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(150) NOT NULL,
  `category` VARCHAR(100) NOT NULL,
  `description` TEXT,
  `image_file` VARCHAR(100) DEFAULT 'default.jpg'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Tabel Unit (Stok Detail per Barang)
CREATE TABLE IF NOT EXISTS `unit` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `item_id` INT NOT NULL,
  `serial_number` VARCHAR(50) NOT NULL UNIQUE,
  `status` VARCHAR(20) DEFAULT 'Ready',
  `last_check_in` DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_unit_item` FOREIGN KEY (`item_id`) REFERENCES `item`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Tabel Asset Transaction (Log Riwayat Masuk/Keluar)
CREATE TABLE IF NOT EXISTS `asset_transaction` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `unit_id` INT NOT NULL,
  `type` VARCHAR(10) NOT NULL,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `notes` VARCHAR(255),
  `admin_id` INT,
  CONSTRAINT `fk_trans_unit` FOREIGN KEY (`unit_id`) REFERENCES `unit`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_trans_admin` FOREIGN KEY (`admin_id`) REFERENCES `user`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
