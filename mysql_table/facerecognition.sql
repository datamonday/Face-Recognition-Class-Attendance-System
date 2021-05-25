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

 Date: 25/04/2021 23:04:35
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
INSERT INTO `checkin` VALUES ('Neymar', 11, '2020002', '2020-05-25 00:20:55', '迟到');
INSERT INTO `checkin` VALUES ('Messi', 10, '2020001', '2021-04-25 22:31:48', '请假');

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
INSERT INTO `students` VALUES (10, 'Messi', '2020001', 'male', '19870624');
INSERT INTO `students` VALUES (11, 'Neymar', '2020002', 'male', '19920205');

SET FOREIGN_KEY_CHECKS = 1;
