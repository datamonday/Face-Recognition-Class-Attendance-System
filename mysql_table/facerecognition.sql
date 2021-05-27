/*
 Navicat Premium Data Transfer

 Source Server         : MySQL
 Source Server Type    : MySQL
 Source Server Version : 80012
 Source Host           : localhost:3306
 Source Schema         : facerecognition

 Target Server Type    : MySQL
 Target Server Version : 80012
 File Encoding         : 65001

 Date: 27/05/2021 13:55:36
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for checkin
-- ----------------------------
DROP TABLE IF EXISTS `checkin`;
CREATE TABLE `checkin`  (
  `Name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `ID` int(11) NULL DEFAULT NULL,
  `Class` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Time` datetime NULL DEFAULT NULL,
  `Description` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of checkin
-- ----------------------------
INSERT INTO `checkin` VALUES ('Messi', 10, '2020001', '2020-05-25 00:20:27', '迟到');
INSERT INTO `checkin` VALUES ('Messi', 10, '2020001', '2021-05-27 01:20:59', '旷课');
INSERT INTO `checkin` VALUES ('Messi', 10, '2020001', '2021-05-27 03:35:03', '旷课');
INSERT INTO `checkin` VALUES ('Messi', 10, '2020001', '2021-05-27 08:58:47', '旷课');
INSERT INTO `checkin` VALUES ('Messi', 10, '2020001', '2021-05-27 10:19:34', '旷课');

-- ----------------------------
-- Table structure for studentnums
-- ----------------------------
DROP TABLE IF EXISTS `studentnums`;
CREATE TABLE `studentnums`  (
  `Class` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Num` int(11) NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of studentnums
-- ----------------------------
INSERT INTO `studentnums` VALUES ('2020001', 23);
INSERT INTO `studentnums` VALUES ('2020002', 24);

-- ----------------------------
-- Table structure for students
-- ----------------------------
DROP TABLE IF EXISTS `students`;
CREATE TABLE `students`  (
  `ID` int(11) NOT NULL,
  `Name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Class` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Sex` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `Birthday` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`ID`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of students
-- ----------------------------
INSERT INTO `students` VALUES (1, 'TerStegen', '2020001', 'male', '19920430');
INSERT INTO `students` VALUES (2, 'Dest', '2020002', 'male', '20001103');
INSERT INTO `students` VALUES (3, 'Pique', '2020001', 'male', '19870202');
INSERT INTO `students` VALUES (4, 'Araújo', '2020002', 'male', '19990307');
INSERT INTO `students` VALUES (5, 'Busquets', '2020001', 'male', '19880716');
INSERT INTO `students` VALUES (6, 'Wijnaldum', '2020002', 'male', '19901111');
INSERT INTO `students` VALUES (7, 'Griezmann', '2020001', 'male', '19910321');
INSERT INTO `students` VALUES (9, 'Kun', '2020002', 'male', '19880602');
INSERT INTO `students` VALUES (10, 'Messi', '2020001', 'male', '19870624');
INSERT INTO `students` VALUES (11, 'Dembélé', '2020001', 'male', '19970515');
INSERT INTO `students` VALUES (12, 'Depay', '2020002', 'male', '19940213');
INSERT INTO `students` VALUES (13, 'Ignacio', '2020002', 'male', '19990302');
INSERT INTO `students` VALUES (14, 'Coutinho', '2020001', 'male', '19920612');
INSERT INTO `students` VALUES (15, 'Lenglet', '2020002', 'male', '19950617');
INSERT INTO `students` VALUES (16, 'Pedri', '2020001', 'male', '20021125');
INSERT INTO `students` VALUES (17, 'Emerson ', '2020001', 'male', '19990114');
INSERT INTO `students` VALUES (18, 'Alba', '2020001', 'male', '19890321');
INSERT INTO `students` VALUES (21, 'Frenkie', '2020001', 'male', '19970512');
INSERT INTO `students` VALUES (22, 'AnsuFati', '2020002', 'male', '20021031');
INSERT INTO `students` VALUES (23, ' Garcia', '2020002', 'male', '20010109');
INSERT INTO `students` VALUES (27, 'Moriba', '2020002', 'male', '20030119');

SET FOREIGN_KEY_CHECKS = 1;
