/**
 * StorageProvider Interface
 * Purpose: Defines contract methods for file uploading and retrieval.
 * Responsibility: Abstract storage logic to prevent code coupling to local disk folders.
 */
class StorageProvider {
  /**
   * Saves a file to the storage medium.
   * @param {object} file Multer file object
   * @returns {Promise<string>} Returns relative URL or cloud URI of the file
   */
  async saveFile(file) {
    throw new Error('Method "saveFile" must be implemented.');
  }

  /**
   * Deletes a file from the storage medium.
   * @param {string} filePath File path or URI to delete
   * @returns {Promise<boolean>} Success confirmation
   */
  async deleteFile(filePath) {
    throw new Error('Method "deleteFile" must be implemented.');
  }
}

module.exports = StorageProvider;
