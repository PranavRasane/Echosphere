import React, { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import './App.css'

// Use your actual Render URL
const API_BASE_URL = 'https://echosphere-803v.onrender.com'

// Configure axios for better performance and CORS
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor for better error handling
api.interceptors.request.use(
  (config) => {
    console.log(
      `Making ${config.method?.toUpperCase()} request to: ${config.url}`
    )
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)

    if (error.code === 'ECONNABORTED') {
      alert('Request timeout. Please try again.')
    } else if (error.response?.status === 429) {
      alert('Too many requests. Please wait a minute.')
    } else if (error.response?.status >= 500) {
      alert('Server error. Please try again later.')
    } else if (error.response?.status === 404) {
      alert('Service temporarily unavailable. Please try again.')
    } else {
      alert('Network error. Please check your connection.')
    }

    return Promise.reject(error)
  }
)

function App() {
  const [brandInput, setBrandInput] = useState('')
  const [brandData, setBrandData] = useState(null)
  const [competitorData, setCompetitorData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [hasError, setHasError] = useState(false)
  const [aiStatus, setAiStatus] = useState(null)
  const [searchHistory, setSearchHistory] = useState([])
  const [activeTab, setActiveTab] = useState('overview')

  // Check AI status - memoized for performance
  const checkAIStatus = useCallback(async () => {
    try {
      console.log('Checking AI status at:', `${API_BASE_URL}/api/ai-status`)
      const response = await api.get('/api/ai-status')
      setAiStatus(response.data)
      console.log('AI Status:', response.data)
    } catch (error) {
      console.warn('AI status check failed:', error)
      setAiStatus({ ai_available: false, status: 'unknown' })
    }
  }, [])

  const handleAnalyzeClick = async () => {
    if (!brandInput.trim()) {
      alert('Please enter a brand name first')
      return
    }

    setIsLoading(true)
    setHasError(false)
    setBrandData(null)
    setCompetitorData(null)

    try {
      console.log('🧠 Analyzing brand:', brandInput)
      console.log('API Base URL:', API_BASE_URL)

      // Test connection first
      await api.get('/api/health')

      // Parallel API calls for better performance
      const [brandResult, competitorResult] = await Promise.all([
        api.post('/api/analyze', {
          brand: brandInput.trim(),
        }),
        api.post('/api/competitors', {
          brand: brandInput.trim(),
        }),
      ])

      console.log('Brand analysis result:', brandResult.data)
      console.log('Competitor analysis result:', competitorResult.data)

      setBrandData(brandResult.data)
      setCompetitorData(competitorResult.data)

      // Update search history
      setSearchHistory((prev) => {
        const newHistory = [
          brandInput.trim(),
          ...prev.filter((item) => item !== brandInput.trim()),
        ]
        return newHistory.slice(0, 5) // Keep only last 5 searches
      })
    } catch (error) {
      console.error('❌ Analysis failed:', error)
      setHasError(true)
    } finally {
      setIsLoading(false)
    }
  }

  // Load search history from localStorage on component mount
  useEffect(() => {
    checkAIStatus()

    const savedHistory = localStorage.getItem('echosphere_search_history')
    if (savedHistory) {
      setSearchHistory(JSON.parse(savedHistory))
    }

    // Test backend connection on app start
    const testConnection = async () => {
      try {
        const response = await api.get('/api/health')
        console.log('Backend connection successful:', response.data)
      } catch (error) {
        console.error('Backend connection failed:', error)
      }
    }
    testConnection()
  }, [checkAIStatus])

  // Save search history to localStorage when it changes
  useEffect(() => {
    if (searchHistory.length > 0) {
      localStorage.setItem(
        'echosphere_search_history',
        JSON.stringify(searchHistory)
      )
    }
  }, [searchHistory])

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleAnalyzeClick()
    }
  }

  const handleBrandSelect = (brand) => {
    setBrandInput(brand)
    // Auto-analyze when selecting from history
    setTimeout(() => handleAnalyzeClick(), 100)
  }

  const handleRetry = () => {
    setHasError(false)
    if (brandInput.trim()) {
      handleAnalyzeClick()
    }
  }

  // Utility functions optimized for new design
  const getColorForSentiment = (type) => {
    const colors = {
      positive: '#10b981', // Success green
      negative: '#ef4444', // Error red
      neutral: '#94a3b8', // Muted blue-gray
    }
    return colors[type] || colors.neutral
  }

  const calculateRiskLevel = () => {
    if (!brandData?.mentions) return 'low'

    const negativeMentions = brandData.mentions.filter(
      (m) => m.sentiment === 'negative'
    ).length
    const totalMentions = brandData.mentions.length
    const negativePercentage =
      totalMentions > 0 ? (negativeMentions / totalMentions) * 100 : 0

    if (negativePercentage > 30) return 'high'
    if (negativePercentage > 15) return 'medium'
    return 'low'
  }
  // For Future purpose:

  /*const getColorForRisk = (level) => {
    const colors = {
      high: '#ef4444', // Red
      medium: '#f59e0b', // Amber
      low: '#10b981', // Emerald
    }
    return colors[level] || colors.low
  } */

  const getRiskIcon = (level) => {
    const icons = {
      high: '🔴',
      medium: '🟡',
      low: '🟢',
    }
    return icons[level] || icons.low
  }

  const calculateSentimentScore = () => {
    if (!brandData?.mentions) return 0
    const positiveMentions = brandData.mentions.filter(
      (m) => m.sentiment === 'positive'
    ).length
    const totalMentions = brandData.mentions.length
    return totalMentions > 0
      ? Math.round((positiveMentions / totalMentions) * 100)
      : 0
  }

  const calculateRiskScore = () => {
    if (!brandData?.mentions) return 0
    const negativeMentions = brandData.mentions.filter(
      (m) => m.sentiment === 'negative'
    ).length
    const totalMentions = brandData.mentions.length
    const negativePercentage =
      totalMentions > 0 ? (negativeMentions / totalMentions) * 100 : 0
    return Math.min(100, Math.round(negativePercentage * 2))
  }

  // Derived values
  const riskLevel = calculateRiskLevel()
  const sentimentScore = calculateSentimentScore()
  const riskScore = calculateRiskScore()
  const totalMentions = brandData?.mentions?.length || 0
  const brandName = brandData?.brand || 'Unknown Brand'

  if (isLoading) {
    return (
      <div className="app">
        <header className="header">
          <h1>🌐 Echosphere</h1>
          <p>Intelligent Brand Reputation Monitoring</p>
          <div className="connection-status">
            <div className="status-indicator disconnected">●</div>
            <span>Analyzing in progress...</span>
          </div>
        </header>

        <div className="loading-section">
          <div className="loading-spinner"></div>
          <p>Scanning digital landscape for {brandInput}</p>
          <p className="loading-subtitle">
            Analyzing sentiment patterns and competitor positioning
          </p>
        </div>
      </div>
    )
  }

  if (hasError) {
    return (
      <div className="app">
        <header className="header">
          <h1>🌐 Echosphere</h1>
          <p>Intelligent Brand Reputation Monitoring</p>
        </header>

        <div className="error-section">
          <div className="error-icon">⚠️</div>
          <h2>Connection Issue</h2>
          <p>Couldn't reach the analysis server.</p>
          <p>Please check your connection and try again.</p>
          <button onClick={handleRetry} className="retry-button">
            Try Again
          </button>
          <button
            onClick={() => setHasError(false)}
            className="retry-button secondary"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🌐 Echosphere</h1>
        <p>Intelligent Brand Reputation Monitoring</p>

        {/* Connection Status */}
        <div className="connection-status">
          <div
            className={`status-indicator ${
              aiStatus?.ai_available ? 'connected' : 'disconnected'
            }`}
          >
            ●
          </div>
          <span>
            {aiStatus?.ai_available
              ? 'AI Analysis Active'
              : 'Enhanced Analysis Mode'}
          </span>
        </div>
      </header>

      <section className="search-section">
        <div className="search-container">
          <div className="search-box">
            <input
              type="text"
              placeholder="Enter brand name: Nike, Starbucks, Apple, Samsung..."
              value={brandInput}
              onChange={(e) => setBrandInput(e.target.value)}
              onKeyPress={handleKeyPress}
              className="brand-input"
              list="search-history"
            />
            <datalist id="search-history">
              {searchHistory.map((brand, index) => (
                <option key={index} value={brand} />
              ))}
            </datalist>
            <button
              onClick={handleAnalyzeClick}
              className="analyze-button"
              disabled={isLoading}
            >
              {isLoading ? 'Analyzing...' : 'Analyze Brand'}
            </button>
          </div>

          {searchHistory.length > 0 && (
            <div className="search-suggestions">
              <span className="suggestions-label">Recent searches:</span>
              {searchHistory.map((brand, index) => (
                <button
                  key={index}
                  className="suggestion-chip"
                  onClick={() => handleBrandSelect(brand)}
                >
                  {brand}
                </button>
              ))}
            </div>
          )}
        </div>
      </section>

      {brandData ? (
        <main className="results-section">
          {/* AI Status Banner */}
          {aiStatus && (
            <div className="ai-status-banner">
              <div
                className={`ai-status ${
                  aiStatus.ai_available ? 'active' : 'fallback'
                }`}
              >
                <span className="ai-icon">
                  {aiStatus.ai_available ? '🧠' : '⚡'}
                </span>
                <span className="ai-text">
                  {aiStatus.ai_available
                    ? 'Powered by Advanced AI Analysis'
                    : 'Enhanced Pattern Recognition Analysis'}
                </span>
                <span className="ai-confidence">
                  {brandData?.summary?.ai_confidence_avg &&
                    `Confidence: ${brandData.summary.ai_confidence_avg}%`}
                </span>
              </div>
            </div>
          )}

          {/* Navigation Tabs */}
          <div className="results-tabs">
            <button
              className={`tab-button ${
                activeTab === 'overview' ? 'active' : ''
              }`}
              onClick={() => setActiveTab('overview')}
            >
              📊 Overview
            </button>
            <button
              className={`tab-button ${
                activeTab === 'mentions' ? 'active' : ''
              }`}
              onClick={() => setActiveTab('mentions')}
            >
              💬 Mentions ({totalMentions})
            </button>
            <button
              className={`tab-button ${
                activeTab === 'competitors' ? 'active' : ''
              }`}
              onClick={() => setActiveTab('competitors')}
            >
              ⚔️ Competitors
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className="tab-content">
              {/* Summary cards */}
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-icon">📊</div>
                  <h3>Total Mentions</h3>
                  <div className="metric-value">{totalMentions}</div>
                  <p>Across all platforms</p>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">😊</div>
                  <h3>Sentiment Score</h3>
                  <div className="metric-value">{sentimentScore}%</div>
                  <p>Positive mentions</p>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">⚠️</div>
                  <h3>Risk Level</h3>
                  <div className="metric-value">
                    {getRiskIcon(riskLevel)} {riskLevel.toUpperCase()}
                  </div>
                  <p>Current brand health</p>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">📈</div>
                  <h3>Risk Score</h3>
                  <div className="metric-value">{riskScore}/100</div>
                  <p>Lower is better</p>
                </div>
              </div>

              {/* Crisis Alerts */}
              {riskLevel === 'high' && (
                <div className="warning-banner">
                  <span className="warning-icon">🚨</span>
                  <div className="warning-text">
                    <strong>High Alert:</strong> Significant negative sentiment
                    detected. Immediate brand management recommended.
                  </div>
                </div>
              )}

              {riskLevel === 'medium' && (
                <div className="warning-banner medium">
                  <span className="warning-icon">⚠️</span>
                  <div className="warning-text">
                    <strong>Medium Alert:</strong> Elevated negative sentiment
                    detected. Proactive monitoring advised.
                  </div>
                </div>
              )}

              {/* Quick Stats */}
              <div className="quick-stats">
                <h3>Performance Metrics for {brandName}</h3>
                <div className="stats-grid">
                  <div className="stat-item">
                    <span className="stat-label">Positive Mentions</span>
                    <span className="stat-value">
                      {brandData.summary.positive_mentions}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Negative Mentions</span>
                    <span className="stat-value">
                      {brandData.summary.negative_mentions}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Analysis Confidence</span>
                    <span className="stat-value">
                      {brandData.summary.ai_confidence_avg}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'mentions' && (
            <div className="tab-content">
              <section className="mentions-section">
                <h2>Brand Conversations About {brandName}</h2>

                <div className="mentions-list">
                  {brandData.mentions.map((mention) => (
                    <div key={mention.id} className="mention-item">
                      <div className="mention-header">
                        <span className="platform">
                          {mention.platform === 'Twitter' && '🐦 Twitter'}
                          {mention.platform === 'Instagram' && '📸 Instagram'}
                          {mention.platform === 'Reddit' && '👥 Reddit'}
                          {mention.platform === 'News' && '📰 News'}
                          {mention.platform === 'Forum' && '💬 Forum'}
                          {mention.platform === 'Blog' && '📝 Blog'}
                          {mention.platform || '🌐 Social'}
                        </span>

                        <span
                          className="sentiment-tag"
                          style={{
                            backgroundColor: getColorForSentiment(
                              mention.sentiment
                            ),
                          }}
                        >
                          {mention.sentiment || 'neutral'}
                        </span>

                        {mention.confidence && (
                          <span className="confidence-badge">
                            {mention.confidence}% conf
                          </span>
                        )}
                      </div>

                      <p className="mention-content">
                        {mention.text || 'No content available'}
                      </p>

                      <div className="mention-footer">
                        <span className="user">
                          👤 {mention.username || 'anonymous'}
                          {mention.verified && ' ✓'}
                        </span>
                        <span className="engagement">
                          ❤️ {mention.engagement || 0}
                        </span>
                        <span className="mood">
                          {mention.emotion === 'anger' && '😠'}
                          {mention.emotion === 'excitement' && '🎉'}
                          {mention.emotion === 'joy' && '😊'}
                          {mention.emotion === 'frustration' && '😤'}
                          {mention.emotion === 'surprise' && '😲'}
                          {mention.emotion || '😐'} {mention.emotion}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          )}

          {activeTab === 'competitors' && competitorData && (
            <div className="tab-content">
              <section className="competitor-section">
                <h2>Competitive Landscape: {brandName}</h2>
                <p className="section-subtitle">
                  Market position analysis compared to key competitors
                </p>

                <div className="competitor-comparison">
                  {/* Main Brand - Featured Card */}
                  <div className="competitor-featured">
                    <div className="featured-card main-brand">
                      <div className="brand-header">
                        <h3>{competitorData.main_brand.name}</h3>
                        <div className="primary-badge">Your Brand</div>
                      </div>
                      <div className="metrics-grid">
                        <div className="metric-item">
                          <div className="metric-icon">📊</div>
                          <div className="metric-info">
                            <span className="metric-value">
                              {competitorData.main_brand.mentions}
                            </span>
                            <span className="metric-label">Mentions</span>
                          </div>
                        </div>
                        <div className="metric-item">
                          <div className="metric-icon">😊</div>
                          <div className="metric-info">
                            <span className="metric-value">
                              {competitorData.main_brand.sentiment_score}%
                            </span>
                            <span className="metric-label">Sentiment</span>
                          </div>
                        </div>
                        <div className="metric-item">
                          <div className="metric-icon">🏆</div>
                          <div className="metric-info">
                            <span className="metric-value">
                              {competitorData.main_brand.market_share || '25'}%
                            </span>
                            <span className="metric-label">Market Share</span>
                          </div>
                        </div>
                      </div>
                      <div className="performance-summary">
                        <div className="summary-text">
                          {competitorData.main_brand.sentiment_score > 75
                            ? 'Strong'
                            : competitorData.main_brand.sentiment_score > 50
                            ? 'Stable'
                            : 'Needs Attention'}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Competitors List */}
                  <div className="competitors-list">
                    <h4 className="competitors-title">Key Competitors</h4>
                    <div className="competitors-grid">
                      {competitorData.competitors.map((competitor, index) => {
                        const isBetter =
                          competitor.sentiment_score >
                          competitorData.main_brand.sentiment_score
                        const sentimentDiff =
                          competitor.sentiment_score -
                          competitorData.main_brand.sentiment_score

                        return (
                          <div key={index} className="competitor-card">
                            <div className="card-header">
                              <h4>{competitor.name}</h4>
                              <div
                                className={`trend-badge ${
                                  isBetter ? 'negative' : 'positive'
                                }`}
                              >
                                {isBetter ? '📈 Threat' : '📉 Behind'}
                              </div>
                            </div>

                            <div className="competitor-metrics">
                              <div className="metric-row">
                                <span className="metric-name">Mentions</span>
                                <span className="metric-value">
                                  {competitor.mentions}
                                </span>
                              </div>
                              <div className="metric-row">
                                <span className="metric-name">Sentiment</span>
                                <span className="metric-value">
                                  {competitor.sentiment_score}%
                                </span>
                              </div>
                              <div className="metric-row">
                                <span className="metric-name">
                                  Vs. Your Brand
                                </span>
                                <span
                                  className={`difference ${
                                    isBetter ? 'negative' : 'positive'
                                  }`}
                                >
                                  {isBetter ? '+' : ''}
                                  {sentimentDiff}%
                                </span>
                              </div>
                            </div>

                            <div className="threat-level">
                              <div className="threat-label">
                                Threat Level:
                                <span
                                  className={`level ${
                                    competitor.threat_level || 'medium'
                                  }`}
                                >
                                  {competitor.threat_level || 'medium'}
                                </span>
                              </div>
                              <div className="trend-status">
                                {competitor.trend === 'rising'
                                  ? '↗ Rising'
                                  : competitor.trend === 'declining'
                                  ? '↘ Declining'
                                  : '→ Stable'}
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                </div>
              </section>
            </div>
          )}
        </main>
      ) : (
        <section className="features-section">
          <h2>Intelligent Brand Monitoring Platform</h2>
          <p className="features-intro">
            Echosphere provides comprehensive brand intelligence by analyzing
            digital conversations across social media, news platforms, and
            forums to deliver actionable insights.
          </p>

          <div className="features-grid">
            <div className="feature">
              <div className="feature-icon">🔍</div>
              <h3>Comprehensive Monitoring</h3>
              <p>
                Track brand mentions across all digital channels and platforms
              </p>
            </div>

            <div className="feature">
              <div className="feature-icon">😊</div>
              <h3>Sentiment Intelligence</h3>
              <p>Advanced analysis of customer emotions and brand perception</p>
            </div>

            <div className="feature">
              <div className="feature-icon">🚨</div>
              <h3>Risk Detection</h3>
              <p>Early warning system for potential brand reputation issues</p>
            </div>

            <div className="feature">
              <div className="feature-icon">⚔️</div>
              <h3>Competitive Insights</h3>
              <p>Benchmark performance against industry competitors</p>
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="app-footer">
        <p>
          Echosphere v2.0 | Intelligent Brand Analytics Platform | Built for
          RapidQuest Hackathon 2025
        </p>
      </footer>
    </div>
  )
}

export default App
