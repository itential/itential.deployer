#!/bin/bash
# nexus_mirror_discovery.sh
# Discovers mirrors, redirects, and CDN endpoints for upstream repositories

set -eo pipefail

# Color output for terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Output files
MARKDOWN_OUTPUT="mirror_discovery_$(date +%Y%m%d_%H%M%S).md"
CSV_OUTPUT="mirror_discovery_$(date +%Y%m%d_%H%M%S).csv"

# URL definitions - format: "name|url"
URLS=(
    "PyPI|https://pypi.org/simple/"
    "Ansible_Galaxy|https://galaxy.ansible.com/api/"
    "Itential_Registry|https://registry.aws.itential.com"
    "NPM_Registry|https://registry.npmjs.org/"
    "GitHub|https://github.com"
    "GitHub_Codeload|https://codeload.github.com"
    "MongoDB_Repo|https://repo.mongodb.org/yum/redhat/8/mongodb-org/7.0/x86_64/"
    "MongoDB_WWW|https://www.mongodb.org"
    "MongoDB_GPG_org|https://pgp.mongodb.org/server-7.0.asc"
    "MongoDB_GPG_com|https://pgp.mongodb.com/server-7.0.asc"
    "Remi_Repo|http://rpms.remirepo.net/enterprise/8/remi/x86_64/"
    "Fedora_EPEL|https://dl.fedoraproject.org/pub/epel/8/Everything/x86_64/"
    "HashiCorp_Vault|https://rpm.releases.hashicorp.com/RHEL/8/x86_64/stable/"
)

# Function to extract domain from URL
extract_domain() {
    echo "$1" | awk -F[/:] '{print $4}'
}

# Function to check DNS resolution
check_dns() {
    local domain="$1"
    local result
    
    # Get A records
    result=$(dig +short "$domain" A 2>/dev/null | head -5 | tr '\n' ',' | sed 's/,$//')
    if [ -z "$result" ]; then
        echo "No A records"
        return
    fi
    
    # Check for CNAME
    local cname=$(dig +short "$domain" CNAME 2>/dev/null | tr '\n' ',' | sed 's/,$//')
    if [ -n "$cname" ]; then
        echo "CNAME: $cname - IPs: $result"
    else
        echo "Direct: $result"
    fi
}

# Function to check HTTP redirects
check_redirects() {
    local url="$1"
    local output
    
    # Follow redirects and capture headers
    output=$(curl -sIL -m 10 "$url" 2>/dev/null || echo "CURL_ERROR")
    
    if [ "$output" = "CURL_ERROR" ]; then
        echo "Connection failed"
        return 1
    fi
    
    # Extract all Location headers
    local locations=$(echo "$output" | grep -i "^Location:" | sed 's/Location: //i' | tr -d '\r')
    
    if [ -n "$locations" ]; then
        echo "$locations"
    else
        echo "No redirects"
    fi
}

# Function to identify CDN
identify_cdn() {
    local url="$1"
    local headers
    
    headers=$(curl -sI -m 10 "$url" 2>/dev/null || echo "")
    
    # Check common CDN headers
    if echo "$headers" | grep -qi "x-amz-cf-id\|cloudfront"; then
        echo "CloudFront"
    elif echo "$headers" | grep -qi "x-cache.*fastly\|fastly"; then
        echo "Fastly"
    elif echo "$headers" | grep -qi "x-akamai\|akamai"; then
        echo "Akamai"
    elif echo "$headers" | grep -qi "x-cache.*cloudflare\|cf-ray"; then
        echo "Cloudflare"
    elif echo "$headers" | grep -qi "x-served-by.*varnish"; then
        echo "Varnish Cache"
    else
        echo "Unknown/Direct"
    fi
}

# Function to check if URL requires authentication
check_auth() {
    local url="$1"
    local status
    
    status=$(curl -sI -m 10 "$url" 2>/dev/null | grep "^HTTP" | tail -1 | awk '{print $2}')
    
    case "$status" in
        200|301|302|303|307|308)
            echo "Public"
            ;;
        401|403)
            echo "Auth Required"
            ;;
        *)
            echo "Unknown ($status)"
            ;;
    esac
}

# Initialize output files
cat > "$MARKDOWN_OUTPUT" << EOF
# Nexus Upstream Mirror Discovery Report

**Generated:** $(date '+%Y-%m-%d %H:%M:%S')  
**Purpose:** Document actual mirrors, redirects, and CDN endpoints for Nexus proxy configuration

## Summary

This report identifies the actual endpoints that upstream repositories use, including:
- DNS resolution and CNAMEs
- HTTP redirects
- CDN providers
- Authentication requirements

## Detailed Findings

EOF

cat > "$CSV_OUTPUT" << 'EOF'
"Component","Base URL","DNS Resolution","HTTP Redirects","CDN Provider","Auth Status","Notes"
EOF

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Nexus Upstream Mirror Discovery Tool                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Output files:"
echo -e "  - Markdown: ${GREEN}$MARKDOWN_OUTPUT${NC}"
echo -e "  - CSV:      ${GREEN}$CSV_OUTPUT${NC}"
echo ""

# Process each URL
total=${#URLS[@]}
current=0

for entry in "${URLS[@]}"; do
    current=$((current + 1))
    
    # Split entry into name and url
    name=$(echo "$entry" | cut -d'|' -f1)
    url=$(echo "$entry" | cut -d'|' -f2)
    domain=$(extract_domain "$url")
    
    echo -e "\n${YELLOW}[$current/$total]${NC} Processing: ${GREEN}$name${NC}"
    echo -e "         URL: $url"
    
    # Gather information
    echo -n "         DNS: "
    dns_info=$(check_dns "$domain")
    echo "$dns_info"
    
    echo -n "   Redirects: "
    redirect_info=$(check_redirects "$url")
    echo "$redirect_info"
    
    echo -n "         CDN: "
    cdn_info=$(identify_cdn "$url")
    echo "$cdn_info"
    
    echo -n "        Auth: "
    auth_info=$(check_auth "$url")
    echo "$auth_info"
    
    # Write to Markdown
    cat >> "$MARKDOWN_OUTPUT" << EOF

### $name

**Base URL:** \`$url\`

| Attribute | Value |
|-----------|-------|
| Domain | $domain |
| DNS Resolution | $dns_info |
| HTTP Redirects | $redirect_info |
| CDN Provider | $cdn_info |
| Authentication | $auth_info |

**Nexus Configuration:**
\`\`\`
Remote URL: $url
\`\`\`

EOF

    # Write to CSV (escape quotes and commas)
    dns_csv=$(echo "$dns_info" | tr '\n' ';' | sed 's/"/\\"/g')
    redirect_csv=$(echo "$redirect_info" | tr '\n' ';' | sed 's/"/\\"/g')
    
    echo "\"$name\",\"$url\",\"$dns_csv\",\"$redirect_csv\",\"$cdn_info\",\"$auth_info\",\"\"" >> "$CSV_OUTPUT"
    
    # Small delay to be respectful
    sleep 0.5
done

# Add recommendations section to markdown
cat >> "$MARKDOWN_OUTPUT" << 'EOF'

## Recommendations for Nexus Proxy Configuration

### High Priority Mirrors

Based on the discovery, these repositories should be prioritized for Nexus proxy setup:

1. **PyPI (files.pythonhosted.org)** - High traffic, CDN-backed
2. **NPM Registry** - Frequent updates, large artifact count
3. **MongoDB Repository** - Mission-critical packages
4. **GitHub/Codeload** - Source tarball dependencies

### Configuration Notes

- **Use base URLs** in Nexus proxy configuration (e.g., `https://pypi.org/simple/`)
- Nexus will automatically follow redirects to CDN endpoints
- For repositories with mirrorlists (EPEL), use the primary URL
- Configure appropriate cache TTLs based on update frequency

### Authentication Requirements

Repositories requiring authentication should be configured with appropriate credentials in Nexus:
- Itential Registry: Requires authentication token
- Private GitHub repositories: Requires PAT or SSH key

### GPG Key Handling

For YUM repositories, import GPG keys separately or host in Nexus raw repository:
- MongoDB: `https://pgp.mongodb.com/server-7.0.asc`
- HashiCorp: Available in repository metadata

EOF

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Discovery Complete!                                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Reports generated:"
echo -e "  📄 Markdown: ${GREEN}$MARKDOWN_OUTPUT${NC}"
echo -e "  📊 CSV:      ${GREEN}$CSV_OUTPUT${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. Review the generated reports"
echo -e "  2. Configure Nexus proxy repositories using base URLs"
echo -e "  3. Test proxy access from your air-gapped environment"
echo -e "  4. Update your Ansible playbooks to use Nexus URLs"
echo ""

# Optional: Display summary table
echo -e "${BLUE}Quick Summary:${NC}"
echo ""
printf "%-25s %-15s %-20s\n" "Component" "CDN Provider" "Auth Status"
echo "───────────────────────────────────────────────────────────────"

for entry in "${URLS[@]}"; do
    name=$(echo "$entry" | cut -d'|' -f1)
    url=$(echo "$entry" | cut -d'|' -f2)
    cdn=$(identify_cdn "$url")
    auth=$(check_auth "$url")
    printf "%-25s %-15s %-20s\n" "$name" "$cdn" "$auth"
done
