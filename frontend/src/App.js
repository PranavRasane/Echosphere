import React, { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import './App.css'

// Use your actual Render URL
const API_BASE_URL =
  process.env.REACT_APP_API_URL || 'https://echosphere-803v.onrender.com'

// Configure axios for better performance
axios.defaults.timeout = 15000
axios.defaults.headers.common['Content-Type'] = 'application/json'

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
      const response = await axios.get(`${API_BASE_URL}/api/ai-status`)
      setAiStatus(response.data)
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

      // Parallel API calls for better performance
      const [brandResult, competitorResult] = await Promise.all([
        axios.post(`${API_BASE_URL}/api/analyze`, {
          brand: brandInput.trim(),
        }),
        axios.post(`${API_BASE_URL}/api/competitors`, {
          brand: brandInput.trim(),
        }),
      ])

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

      // Better error messages
      if (error.code === 'ECONNABORTED') {
        alert('Request timeout. The server is taking too long to respond.')
      } else if (error.response?.status >= 500) {
        alert('Server error. Please try again later.')
      } else {
        alert(
          'Unable to connect to the analysis service. Please check your connection.'
        )
      }
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
  }

  const handleRetry = () => {
    setHasError(false)
    if (brandInput.trim()) {
      handleAnalyzeClick()
    }
  }

  // Utility functions
  const getColorForSentiment = (type) => {
    const colors = {
      positive: '#10b981',
      negative: '#ef4444',
      neutral: '#6b7280',
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

  const getColorForRisk = (level) => {
    const colors = {
      high: '#ef4444',
      medium: '#f59e0b',
      low: '#10b981',
    }
    return colors[level] || colors.low
  }

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
          <p>Listening to your brand's digital heartbeat</p>
        </header>

        <div className="loading-section">
          <div className="loading-spinner"></div>
          <p>Scanning the web for {brandInput} mentions...</p>
          <p className="loading-subtitle">
            Analyzing competitors and market position
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
          <p>Listening to your brand's digital heartbeat</p>
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
        <p>Capturing every echo of your brand across the digital sphere</p>
      </header>

      <section className="search-section">
        <div className="search-container">
          <div className="search-box">
            <input
              type="text"
              placeholder="Try: Nike, Starbucks, Apple, Samsung..."
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
                    ? 'Powered by Real AI Analysis'
                    : 'Enhanced Keyword Analysis'}
                </span>
                <span className="ai-confidence">
                  {brandData?.summary?.ai_confidence_avg &&
                    `Avg Confidence: ${brandData.summary.ai_confidence_avg}%`}
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
                  <div
                    className="metric-value"
                    style={{ color: getColorForSentiment('positive') }}
                  >
                    {sentimentScore}%
                  </div>
                  <p>Positive mentions</p>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">⚠️</div>
                  <h3>Risk Level</h3>
                  <div
                    className="metric-value"
                    style={{ color: getColorForRisk(riskLevel) }}
                  >
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
                    <strong>High Alert:</strong> We're detecting significant
                    negative sentiment. Immediate attention recommended.
                  </div>
                </div>
              )}

              {riskLevel === 'medium' && (
                <div className="warning-banner medium">
                  <span className="warning-icon">⚠️</span>
                  <div className="warning-text">
                    <strong>Medium Alert:</strong> Elevated negative sentiment
                    detected. Monitor closely.
                  </div>
                </div>
              )}

              {/* Quick Stats */}
              <div className="quick-stats">
                <h3>Quick Stats for {brandName}</h3>
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
                    <span className="stat-label">AI Confidence</span>
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
                <h2>What People Are Saying About {brandName}</h2>

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
                            color: 'white',
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
                          ❤️ {mention.engagement || 0} likes
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
                <h2>How {brandName} Stacks Up Against Competitors</h2>

                <div className="competitor-grid">
                  <div className="competitor-card main-brand">
                    <h3>{competitorData.main_brand.name}</h3>
                    <div className="competitor-metric">
                      <span className="metric-label">Mentions:</span>
                      <span className="metric-value">
                        {competitorData.main_brand.mentions}
                      </span>
                    </div>
                    <div className="competitor-metric">
                      <span className="metric-label">Sentiment:</span>
                      <span
                        className="metric-value"
                        style={{ color: getColorForSentiment('positive') }}
                      >
                        {competitorData.main_brand.sentiment_score}%
                      </span>
                    </div>
                    <div className="performance-badge">Your Brand</div>
                  </div>

                  {competitorData.competitors.map((competitor, index) => (
                    <div key={index} className="competitor-card">
                      <h3>{competitor.name}</h3>
                      <div className="competitor-metric">
                        <span className="metric-label">Mentions:</span>
                        <span className="metric-value">
                          {competitor.mentions}
                        </span>
                      </div>
                      <div className="competitor-metric">
                        <span className="metric-label">Sentiment:</span>
                        <span
                          className="metric-value"
                          style={{ color: getColorForSentiment('positive') }}
                        >
                          {competitor.sentiment_score}%
                        </span>
                      </div>
                      <div className="trend-indicator">
                        {competitor.sentiment_score >
                        competitorData.main_brand.sentiment_score
                          ? '📈'
                          : '📉'}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          )}
        </main>
      ) : (
        <section className="features-section">
          <h2>See Your Brand Through Our Eyes</h2>
          <p className="features-intro">
            Echosphere helps you understand what the internet is saying about
            your brand. We scan social media, news sites, and forums to give you
            the full picture.
          </p>

          <div className="features-grid">
            <div className="feature">
              <div className="feature-icon">🔍</div>
              <h3>Find Every Mention</h3>
              <p>We search everywhere people talk about brands</p>
            </div>

            <div className="feature">
              <div className="feature-icon">😊</div>
              <h3>Understand Feelings</h3>
              <p>See if people are happy, angry, or just talking</p>
            </div>

            <div className="feature">
              <div className="feature-icon">🚨</div>
              <h3>Spot Problems Early</h3>
              <p>Get alerts before small issues become big ones</p>
            </div>

            <div className="feature">
              <div className="feature-icon">⚔️</div>
              <h3>Beat Competitors</h3>
              <p>See how you stack up against the competition</p>
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="app-footer">
        <p>Built with ❤️ for RapidQuest Hackathon | Echosphere 2025</p>
      </footer>
    </div>
  )
}

export default App
