const fs = require('fs');
const path = require('path');

class IconService {
  constructor() {
    this.iconManifest = null;
    this.iconMap = new Map();
    this.loadManifest();
  }

  loadManifest() {
    try {
      const manifestPath = path.join(__dirname, '../../public/icons/manifest.json');
      const manifestData = fs.readFileSync(manifestPath, 'utf8');
      // Remove BOM if present
      const cleanData = manifestData.replace(/^\uFEFF/, '');
      this.iconManifest = JSON.parse(cleanData);
      
      // Create a flat map of all icons for quick lookup
      Object.keys(this.iconManifest).forEach(category => {
        this.iconManifest[category].forEach(iconPath => {
          const iconName = path.basename(iconPath, '.svg');
          this.iconMap.set(iconName.toLowerCase(), iconName);
        });
      });
      
      console.log(`[IconService] Loaded ${this.iconMap.size} icons from manifest`);
    } catch (error) {
      console.error('[IconService] Failed to load icon manifest:', error.message);
      this.iconManifest = { AWS: [], Azure: [], GCP: [], Others: [] };
    }
  }

  // Check if an icon exists (case-insensitive)
  iconExists(iconName) {
    if (!iconName) return false;
    return this.iconMap.has(iconName.toLowerCase());
  }

  // Get the correct case for an icon name
  getCorrectIconName(iconName) {
    if (!iconName) return null;
    const lowerName = iconName.toLowerCase();
    return this.iconMap.get(lowerName) || null;
  }

  // Find best matching icon for a service
  findBestMatch(serviceName) {
    if (!serviceName) return 'cloud';
    
    const cleanName = serviceName.toLowerCase().replace(/[-_\s]/g, '');
    
    // Direct match
    let match = this.iconMap.get(cleanName);
    if (match) return match;
    
    // Partial matches
    const partialMatches = [];
    for (const [iconName, correctName] of this.iconMap.entries()) {
      if (iconName.includes(cleanName) || cleanName.includes(iconName)) {
        partialMatches.push(correctName);
      }
    }
    
    if (partialMatches.length > 0) {
      return partialMatches[0]; // Return first match
    }
    
    // Common service mappings
    const commonMappings = {
      'database': 'RDS',
      'db': 'RDS', 
      'mysql': 'RDS',
      'postgres': 'RDS',
      'sql': 'RDS',
      'nosql': 'DynamoDB',
      'mongodb': 'DocumentDB',
      'redis': 'ElastiCache',
      'cache': 'ElastiCache',
      'server': 'EC2',
      'compute': 'EC2',
      'vm': 'EC2',
      'container': 'ContainerInstances',
      'docker': 'ContainerInstances',
      'kubernetes': 'GoogleKubernetesEngine',
      'k8s': 'GoogleKubernetesEngine',
      'loadbalancer': 'ElasticLoadBalancing',
      'lb': 'ElasticLoadBalancing',
      'alb': 'ElasticLoadBalancing',
      'nlb': 'ElasticLoadBalancing',
      'api': 'APIGateway',
      'gateway': 'APIGateway',
      'storage': 'S3',
      'bucket': 'S3',
      'file': 'S3',
      'cdn': 'CloudFront',
      'function': 'Lambda',
      'serverless': 'Lambda',
      'lambda': 'Lambda',
      'queue': 'SimpleQueueService',
      'sqs': 'SimpleQueueService',
      'topic': 'SimpleNotificationService',
      'sns': 'SimpleNotificationService',
      'notification': 'SimpleNotificationService'
    };
    
    const mapping = commonMappings[cleanName];
    if (mapping && this.iconExists(mapping)) {
      return mapping;
    }
    
    // Default fallbacks
    if (serviceName.toLowerCase().includes('user') || serviceName.toLowerCase().includes('client')) {
      return 'device';
    }
    
    return 'cloud'; // Ultimate fallback
  }

  // Validate and correct DSL icons
  validateAndCorrectDSL(dsl) {
    if (!dsl) return dsl;
    
    // Match Node: IconName patterns
    const nodePattern = /Node:\s*([^\s\[]+)/g;
    
    return dsl.replace(nodePattern, (match, iconName) => {
      const bestMatch = this.findBestMatch(iconName);
      return match.replace(iconName, bestMatch);
    });
  }

  // Get available icons by category
  getAvailableIcons() {
    return this.iconManifest;
  }

  // Get icon statistics
  getStats() {
    const stats = {
      totalIcons: this.iconMap.size,
      categories: {}
    };
    
    Object.keys(this.iconManifest || {}).forEach(category => {
      stats.categories[category] = (this.iconManifest[category] || []).length;
    });
    
    return stats;
  }
}

// Export singleton instance
module.exports = new IconService();